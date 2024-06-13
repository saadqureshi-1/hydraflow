from langchain_community.llms import Ollama

llm = Ollama(
    base_url = "http://192.168.110.5:11434",
    model="phi3"
)  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `

print(llm.invoke("Tell me a joke"))
