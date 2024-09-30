from locust import HttpUser, task, between
import json
import random
import time

# Load messages from a file and store them in a list
def load_messages(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Load the input messages from 'messages.txt'
messages = load_messages('./test/input_messages.txt')

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # Random wait time between requests

    @task
    def send_and_check_request(self):
        # Randomly select a message from the loaded messages
        if messages:
            message = random.choice(messages)
        else:
            message = "Default test message"  # Fallback message if the file is empty or not loaded

        # Define the payload with the selected message
        payload = {
            "message": message
        }

        # Use Locust's context manager to measure the total duration of the full request flow
        with self.environment.events.request.measure("FULL", "submit_and_check") as request_meta:
            # Submit the request and get the request_id (no individual tracking)
            response = self.client.post("/submit_request", data=json.dumps(payload), headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                request_id = response.json().get("request_id")
                if request_id:
                    status = None
                    while status != "completed":
                        time.sleep(2)
                        
                        # Check the request status (no individual tracking)
                        status_response = self.client.get(f"/check_status/{request_id}")
                        if status_response.status_code == 200:
                            status = status_response.json().get("status")
                        else:
                            request_meta.success = False
                            break
            else:
                request_meta.success = False
