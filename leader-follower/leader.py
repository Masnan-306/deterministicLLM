from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from pydantic import BaseModel, Field
import uuid
import json
import os
from dapr.clients import DaprClient
import asyncio

app = FastAPI()
dapr_app = DaprApp(app)

PUBSUB_NAME = 'llm-pubsub'
REGISTRATION_TOPIC = 'follower-registration'
RESPONSE_TOPIC = 'llm-responses'
STATE_STORE_NAME = 'statestore'
FOLLOWER_IDS = []
ROUND_ROBIN_COUNT = 0

class LLMPrompt(BaseModel):
    message: str = Field(..., description="Input message for the LLM")
    
class ResponseEventData(BaseModel):
    request_id: str
    response: str    
    
class FollowerRegistration(BaseModel):
    follower_id: str

class ResponseEvent(BaseModel):
    data: ResponseEventData

class FollowerRegistrationEvent(BaseModel):
    data: FollowerRegistration

def assign_task_to_follower():
    # Assign the task to a follower based on a simple round-robin
    global ROUND_ROBIN_COUNT
    
    follower_count = len(FOLLOWER_IDS)
    follower_id = FOLLOWER_IDS[ROUND_ROBIN_COUNT]
    ROUND_ROBIN_COUNT = (ROUND_ROBIN_COUNT + 1) % follower_count
    
    return follower_id

@app.post("/submit_request")
async def submit_request(message: LLMPrompt):
    request_id = str(uuid.uuid4())

    with DaprClient() as client:
        client.save_state(
            store_name=STATE_STORE_NAME,
            key=request_id,
            value=json.dumps({
                "status": "pending",
                "response": None
            }),
        )

        # Assign the task to a specific follower
        follower_id = assign_task_to_follower()

        # Submit the request to the Pub/Sub topic, specifying the follower ID
        client.publish_event(
            pubsub_name=PUBSUB_NAME,
            topic_name=f"tasks/{follower_id}",
            data=json.dumps({
                "request_id": request_id,
                "message": message.message,
            }),
            data_content_type='application/json'
        )

    return {"request_id": request_id}

@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=RESPONSE_TOPIC)
async def handle_response(event: ResponseEvent):
    request_id = event.data.request_id
    follower_response = event.data.response
    
    # Save the follower's response in the state store
    with DaprClient() as client:
        client.save_state(
            store_name=STATE_STORE_NAME,
            key=request_id,
            value=json.dumps({
                "status": "completed",
                "response": follower_response
            }),
        )

    return {"status": "SUCCESS"}

@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=REGISTRATION_TOPIC)
async def handle_follower_registration(event: FollowerRegistrationEvent):
    follower_id = event.data.follower_id
    if follower_id not in FOLLOWER_IDS:
        FOLLOWER_IDS.append(follower_id)

@app.get("/check_status/{request_id}")
async def check_status(request_id: str):
    # Function to get state using DaprClient
    with DaprClient() as client:
        result = client.get_state(
            store_name=STATE_STORE_NAME,
            key=request_id
        )

    if result.data:
        state = json.loads(result.data.decode('utf-8'))
        return state
    else:
        return {"error": "Request not found"}, 404

@app.get("/healthcheck")
def healthcheck():
    return "OK"
