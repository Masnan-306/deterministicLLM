from fastapi import FastAPI, Depends, Body
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError
from llama_cpp import Llama, CreateCompletionResponse
from typing import List, Optional, Union, Iterator, Literal

CONTEXT_SIZE = 512

# Define the input model with message from JSON body
class LLMPrompt(BaseModel):
    message: str = Field(..., description="Input message for the LLM")

    @classmethod
    def check_token_count(cls, v: str) -> str:
        token_count = len(llm.tokenize(v.encode('utf-8')))
        if token_count > CONTEXT_SIZE:
            raise RequestValidationError(
                f"Token count exceeds the maximum allowed limit of {CONTEXT_SIZE}."
            )
        return v

async def get_llm_response(message: LLMPrompt, llm: Llama):
    system_message = "You are a helpful assistant."
    template = f"""<|system|>
    {system_message}</s>
    <|user|>
    {message.message}</s>
    <|assistant|>"""
    llm_response = llm(template, temperature=0.0, max_tokens=64)
    
    choices = llm_response.get("choices", [])
    if choices and isinstance(choices, list):
        return choices[0].get("text", "No text found")
    else:
        return "No choices found in response"

app = FastAPI()

# Load the LLM model
print("Loading tinyllama model...")
llm = Llama.from_pretrained(
    repo_id="TheBloke/Tinyllama-2-1b-miniguanaco-GGUF",
    filename="tinyllama-2-1b-miniguanaco.Q2_K.gguf",
)

@app.post('/chat', response_model=str)
async def send_llm_response(message: LLMPrompt = Body(...)) -> Union[CreateCompletionResponse, Iterator[CreateCompletionResponse]]:
    print(f"Received message: {message.message}")
    model_output = await get_llm_response(message, llm)
    return model_output

@app.get('/healthcheck')
def healthcheck() -> Literal["OK"]:
    return "OK"
