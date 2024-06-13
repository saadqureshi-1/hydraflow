from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

def process_string(input_string: str) -> str:
    # Initialize the ChatGroq model with specified parameters
    chat = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        api_key="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" # Optional if not set as an environment variable
    )

    # Define the system and human messages
    system = "You are a helpful assistant."
    human = "{text}"

    # Create a prompt template from the system and human messages
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    # Create the chain by combining the prompt and the chat model
    chain = prompt | chat

    # Invoke the chain with the input string and get the result
    result = chain.invoke({"text": input_string})
    response_text = result.content 
    # Extract the content of the response to a string
    return response_text

# Example usage
input_str = "Explain the importance of low latency for LLMs."
output = process_string(input_str)
print(output)
