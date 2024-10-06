import json
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from typing import List, Union, Literal
from llama_cpp import Llama

# Define the input model with question and options
class LLMPrompt(BaseModel):
    question: str = Field(..., description="The multiple-choice question to be answered")
    options: List[str] = Field(..., description="List of answer options for the multiple-choice question")

# Define the output model that enforces response to be a single letter
class MCQAnswer(BaseModel):
    answer: str = Field(..., pattern="^[A-Za-z]$", description="Answer should be a single letter (A, B, C, etc.)")

app = FastAPI()

# Load the LLM model
print("Loading Phi-3 model...")
llm = Llama.from_pretrained(
    repo_id="rubra-ai/Phi-3-mini-128k-instruct-GGUF",
    filename="rubra-phi-3-mini-128k-instruct.Q6_K.gguf",
    n_ctx=1024,
)

def parse_llm_response(response) -> str:
    """
    Utility function to parse the LLM response and extract the answer.
    """
    choices = response.get("choices", [])
    if choices and isinstance(choices, list):
        # Extract the arguments as a string
        arguments_str = choices[0].get("message", {}).get("function_call", {}).get("arguments", "")

        # Parse the JSON string to a dictionary
        try:
            answer_data = json.loads(arguments_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse arguments: {e}")

        # Extract the answer
        answer_text = answer_data.get("answer", "").strip()
        
        # Validate the answer
        if len(answer_text) == 1 and answer_text.isalpha():
            return answer_text.upper()
        else:
            raise ValueError("Model response is not a valid single-letter MCQ answer.")
    else:
        raise ValueError("No choices found in response.")

@app.post('/mcq', response_model=MCQAnswer)
async def send_llm_response(message: LLMPrompt = Body(...)) -> MCQAnswer:
    print(f"Received question: {message.question}")
    print(f"Options: {message.options}")

    # Define the system message and tool for the MCQ answering function
    system_message = "A chat between a user asking multiple-choice questions and an AI assistant that responds with a single letter (e.g., A, B, C, etc.). Each letter corresponds to an option sequentially, where A is the first option, B is the second option, and so on."
    user_message = f"Question: {message.question}\nOptions: {', '.join([f'({chr(65+i)}) {option}' for i, option in enumerate(message.options)])}"

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "MCQAnswer",
                "parameters": {
                    "type": "object",
                    "title": "MCQAnswer",
                    "properties": {
                        "answer": {
                            "title": "Answer",
                            "type": "string",
                            "pattern": "^[A-Za-z]$"
                        }
                    },
                    "required": ["answer"]
                }
            }
        }],
        tool_choice={
            "type": "function",
            "function": {
                "name": "MCQAnswer"
            }
        }
    )

    # Parse the LLM response using the utility function
    answer_text = parse_llm_response(response)
    return MCQAnswer(answer=answer_text)

@app.get('/healthcheck')
def healthcheck() -> Literal["OK"]:
    return "OK"