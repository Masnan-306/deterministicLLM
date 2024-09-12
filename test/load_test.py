from locust import HttpUser, task, between
import json
import random

# Load messages from a file and store them in a list
def load_messages(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Load the input messages from 'messages.txt'
messages = load_messages('./test/input_messages.txt')

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # Random wait time between requests

    @task
    def send_chat_request(self):
        # Randomly select a message from the loaded messages
        if messages:
            message = random.choice(messages)
        else:
            message = "Default test message"  # Fallback message if the file is empty or not loaded
        
        # Define the payload with the selected message
        payload = {
            "message": message
        }
        
        # Send a POST request to the /chat endpoint
        with self.client.post("/chat", data=json.dumps(payload), headers={"Content-Type": "application/json"}, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code {response.status_code}")
                

    ###################################################
    # TODO: Replace the host for your own deployment  #
    ###################################################
    host = "http://48.216.168.113"