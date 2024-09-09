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

# Define response models
class Choice(BaseModel):
    text: str = "Beep boop"
    index: int = 0
    logprobs: Optional[str] = "null"
    finish_reason: str = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 198
    completion_tokens: int = 10
    total_tokens: int = 208

class BaseLlamaResponse(BaseModel):
    id: str = "cmpl-7fc1be4c-8f5b-4b2f-805f-f8c5086a9fb4"
    object: str = "text_completion"
    created: int = 1708459650
    model: str = "tinyllama-2-1b-miniguanaco.Q2_K.gguf"
    choices: List[Choice]
    usage: Usage

async def get_llm_response(message: LLMPrompt, llm: Llama) -> Union[CreateCompletionResponse, Iterator[CreateCompletionResponse]]:
    system_message = "You are a helpful assistant."
    template = f"""<|system|>
    {system_message}</s>
    <|user|>
    {message.message}</s>
    <|assistant|>"""
    return llm(template, temperature=0.0, max_tokens=128)

app = FastAPI()

# Load the LLM model
print("Loading tinyllama model...")
llm = Llama.from_pretrained(
    repo_id="TheBloke/Tinyllama-2-1b-miniguanaco-GGUF",
    filename="tinyllama-2-1b-miniguanaco.Q2_K.gguf",
)

@app.post('/api', response_model=BaseLlamaResponse)
async def send_llm_response(message: LLMPrompt = Body(...)) -> Union[CreateCompletionResponse, Iterator[CreateCompletionResponse]]:
    print(f"Received message: {message.message}")
    model_output = await get_llm_response(message, llm)
    return model_output

@app.get('/healthcheck')
def healthcheck() -> Literal["OK"]:
    return "OK"
