import asyncio
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama
import os
import json
from dapr.clients import DaprClient
import uuid

app = FastAPI()
dapr_app = DaprApp(app)

FOLLOWER_ID = uuid.uuid4()
PUBSUB_NAME = 'llm-pubsub'
TOPIC_NAME = 'llm-jobs'
REGISTRATION_TOPIC = 'follower-registration'
RESPONSE_TOPIC = 'llm-responses'

# Load the LLM model
llm = Llama.from_pretrained(
    repo_id="TheBloke/Tinyllama-2-1b-miniguanaco-GGUF",
    filename="tinyllama-2-1b-miniguanaco.Q2_K.gguf",
)

async def register_follower():
    with DaprClient() as client:
        # Publish the follower ID to the registration topic
        client.publish_event(
            pubsub_name=PUBSUB_NAME,
            topic_name=REGISTRATION_TOPIC,
            data=json.dumps({"follower_id": str(FOLLOWER_ID)}),
            data_content_type='application/json'
        )

# Register the follower on startup
@app.on_event("startup")
async def startup_event():
    await register_follower()

class EventData(BaseModel):
    request_id: str
    message: str

class CloudEvent(BaseModel):
    data: EventData

async def process_llm_request(request_id: str, message: str):
    # Format the LLM prompt
    system_message = "You are a helpful assistant."
    template = f"""<|system|>
    {system_message}</s>
    <|user|>
    {message}</s>
    <|assistant|>"""
    
    # Call the LLM for response
    llm_response = llm(template, temperature=0.0, max_tokens=64)
    response_text = llm_response.get("choices", [{}])[0].get("text", "No text found")

    # Publish the result to the leader asynchronously
    with DaprClient() as client:
        client.publish_event(
            pubsub_name=PUBSUB_NAME,
            topic_name=RESPONSE_TOPIC,
            data=json.dumps({
                "request_id": request_id,
                "response": response_text
            }),
            data_content_type='application/json'
        )

@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=f"tasks/{FOLLOWER_ID}")
async def handle_job(event: CloudEvent):
    request_id = event.data.request_id
    message = event.data.message

    # Process the request
    await process_llm_request(request_id, message)
    
    return {"status": "SUCCESS"}

@app.get("/healthcheck")
def healthcheck():
    return "OK"