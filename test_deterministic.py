# test_deterministic.py - Script to test service determinism

import requests

# Set the endpoint of the deployed service
endpoint = "http://<YOUR-SERVICE-LOADBALANCER-IP>:<PORT>/chat/"

# Define the message payload
payload = {
    "message": "Test message to check determinism"
}

# Number of test iterations
num_tests = 10

# Store the first response for comparison
first_response = None
consistent = True

# Test the service multiple times
for i in range(num_tests):
    response = requests.post(endpoint, json=payload)
    if response.status_code == 200:
        response_data = response.json().get("response", None)
        if i == 0:
            first_response = response_data
        elif response_data != first_response:
            consistent = False
            print(f"Test {i+1}: Inconsistent response detected.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Check overall consistency
if consistent:
    print("The service is deterministic: All responses are consistent.")
else:
    print("The service is not deterministic: Some responses differ.")
