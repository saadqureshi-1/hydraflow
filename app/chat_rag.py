import sqlite3
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


def process_string(input_string: str, data: str) -> str:
    """
    Processes the input string using ChatGroq model with the given context data and returns the response.

    :param input_string: The input text string to be processed.
    :param data: A string containing context data for the ChatGroq model.
    :return: The response from the ChatGroq model as a string.
    """
    # Initialize the ChatGroq model with specified parameters
    chat = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        api_key="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"  # Optional if not set as an environment variable
    )

    # Define the system and human messages
    system = """
        - You are a helpful assistant.
        - Provided data is about the user who is being referred to in the query.
        - Assume the data provided is of the user, which might contain some ID.
        - Use the following data for context: {context}.
        - Respond only in markdown.
        - Make sure your response is concise and crisp.
        """

    human = "{text}"

    # Create a prompt template from the system and human messages
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Create the chain by combining the prompt and the chat model
    chain = prompt | chat

    # Invoke the chain with the input string and context data
    result = chain.invoke({"text": input_string, "context": data})
    response_text = result.content

    # Extract the content of the response to a string
    return response_text


def get_sqlite_schema(db_path):
    """
    Connects to an SQLite database and returns the schema for each table as a string.
    
    :param db_path: Path to the SQLite database file.
    :return: A string containing the schema of all tables in the database.
    """
    schema_output = []
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    try:
        # Create a cursor object
        cursor = conn.cursor()
        
        # Get the list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Append the schema for each table to the schema_output list
        for table_name in tables:
            table_name = table_name[0]
            schema_output.append(f"Schema for table: {table_name}\n")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                schema_output.append(f"{column}\n")
            schema_output.append("\n")
    finally:
        # Close the connection
        conn.close()
    
    return ''.join(schema_output)


def generate_sql_query(input_string: str, database_schema: str) -> str:
    """
    Generates an SQLite query based on the input string and database schema using ChatGroq model.
    Ensures the query uses the LIKE feature for email search and returns only the SQL query.

    :param input_string: The input string containing the natural language query.
    :param database_schema: The schema of the SQLite database as a string.
    :return: The generated SQLite query as a string.
    """
    # Initialize the ChatGroq model with specified parameters
    chat = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        api_key="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"  # Optional if not set as an environment variable
    )

    # Define the system and human messages
    # system = "You are a helpful assistant. Generate only an SQLite query based on the provided database schema and input string. Return only the SQL query without any additional text."
    system = "You are a helpful assistant. Generate only an SQLite query based on the provided database schema and input string. Use the LIKE function to search for users in email fields and return only the SQL query without any additional text."
    human = "{text}\nDatabase Schema:\n{schema}"

    # Create a prompt template from the system and human messages
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Create the chain by combining the prompt and the chat model
    chain = prompt | chat

    # Invoke the chain with the input string and database schema
    result = chain.invoke({"text": input_string, "schema": database_schema})
    response_text = result.content.strip()

    # Ensure the query uses the LIKE feature for email searches
    response_text = response_text.replace("WHERE email = ", "WHERE email LIKE ")

    return response_text

def run_sql_query(db_path: str, query: str) -> str:
    """
    Runs the provided SQLite query on the specified database and returns the result as a string.

    :param db_path: Path to the SQLite database file.
    :param query: The SQLite query to be executed.
    :return: The result of the query as a string.
    """
    result_string = ""
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    try:
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        
        # Check if the query returns results
        if cursor.description:
            # Fetch all results
            results = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Format the results as a string
            result_string += "\t".join(column_names) + "\n"
            for row in results:
                result_string += "\t".join(map(str, row)) + "\n"
        else:
            # Handle queries that don't return rows (e.g., INSERT, UPDATE, DELETE)
            conn.commit()
            result_string = "Query executed successfully."
    except Exception as e:
        result_string = str(e)
    finally:
        # Close the connection
        conn.close()
    
    return result_string

def chat_llm(input_string: str) -> str:
    """
    Processes the input string by generating an SQL query, running the query, 
    and using the result in the context for further processing.

    :param input_string: The input text string to be processed.
    :return: The final output as a string.
    """
    # Get the database schema
    database_schema = get_sqlite_schema('instance/db.sqlite3')
    
    # Generate the SQL query based on the input string and database schema
    query = generate_sql_query(input_string, database_schema)
    
    # Print the generated query
    print(query)
    
    # Run the SQL query and get the result
    result = run_sql_query('instance/db.sqlite3', query)
    
    # Process the input string with the result as context
    output = process_string(input_string, result)
    
    return output



