from fastapi import FastAPI, HTTPException
from llama_cpp import Llama
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

# Load the model
llm = Llama.from_pretrained(
    repo_id="TheBloke/Tinyllama-2-1b-miniguanaco-GGUF",
    filename="tinyllama-2-1b-miniguanaco.Q2_K.gguf",
)

# Function to generate responses
def chat_with_model(message):
    llm.reset()
    
    # Initialize conversation history with a system message
    conversation_history = [
        {"role": "system", "content": "You are an AI assistant that helps users with information and conversations. Respond clearly and concisely."},
        {"role": "user", "content": message}
    ]
    
    response = llm.create_chat_completion(
        messages=conversation_history,
        temperature=0,
        seed=123
    )
    
    # Clean up the response by removing unwanted tokens
    output = response["choices"][0]["message"]["content"]
    return output

@app.post("/chat/")
async def chat(message: Message):
    try:
        response = chat_with_model(message.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

