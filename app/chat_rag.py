import sqlite3
import os
from datetime import datetime
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

class SQLiteToChroma:
    def __init__(self, db_path, persist_directory="data", collection_name="sqlite_chroma_demo"):
        self.db_path = db_path
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings()
        self.chroma_db = None
        self.last_updated = None
        self.check_and_update_db()
        
    def check_and_update_db(self):
        last_update_time = self.get_last_update_time()
        if self.is_db_updated(last_update_time):
            self.update_chroma_db()
            self.set_last_update_time()
    
    def get_last_update_time(self):
        try:
            with open('last_update.txt', 'r') as file:
                return datetime.fromisoformat(file.read().strip())
        except FileNotFoundError:
            return None

    def set_last_update_time(self):
        with open('last_update.txt', 'w') as file:
            file.write(datetime.now().isoformat())
    
    def is_db_updated(self, last_update_time):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(updated_at) FROM your_table_name")  # Adjust your query to check for the latest update time
        latest_update = cursor.fetchone()[0]
        conn.close()
        
        if last_update_time is None or latest_update is None:
            return True
        latest_update_time = datetime.fromisoformat(latest_update)
        return latest_update_time > last_update_time
    
    def load_sqlite_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM your_table_name")  # Adjust your query
        rows = cursor.fetchall()
        conn.close()

        documents = [row[0] for row in rows]
        return documents

    def update_chroma_db(self):
        data = self.load_sqlite_data()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
        docs = text_splitter.split_documents(data)

        self.chroma_db = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
    
    def handle_query(self, query):
        if self.chroma_db is None:
            self.check_and_update_db()
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.8)
        chain = RetrievalQA.from_chain_type(llm=llm,
                                            chain_type="stuff",
                                            retriever=self.chroma_db.as_retriever())
        response = chain(query)
        return response

# Usage
db_path = '../database.db'
chat_query = "Summarize"
app = SQLiteToChroma(db_path)
response = app.handle_query(chat_query)
print(response)
