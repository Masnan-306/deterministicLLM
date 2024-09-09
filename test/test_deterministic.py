# test_deterministic.py - Script to test service determinism across different instance types

import requests

# Set the endpoints of the deployed services for different node pools
endpoints = {
    "default": "http://57.152.13.129/chat/",  # Update with the actual IP and port for the default node pool
    "pool1": "http://57.152.15.89/chat/",      # Update with the actual IP and port for pool1
    "pool2": "http://57.152.15.114/chat/"       # Update with the actual IP and port for pool2
}

# Define the message payload
payload = {
    "message": "What is the capital of France?"
}

headers = {
    "Content-Type": "application/json"
}

# Number of test iterations per endpoint
num_tests = 1

# Dictionary to store the first response from each endpoint for comparison
first_responses = {}
overall_consistent = True

# Test the service multiple times across each endpoint
for pool, endpoint in endpoints.items():
    print(f"\nTesting endpoint for {pool} node pool:")
    consistent = True
    first_response = None

    for i in range(num_tests):
        try:
            print("Test", i+1)
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                response_data = response.json().get("response", None)
                if i == 0:
                    first_response = response_data
                    first_responses[pool] = first_response
                elif response_data != first_response:
                    consistent = False
                    print(f"Test {i + 1}: Inconsistent response detected from {pool}.")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error: Request to {endpoint} failed - {e}")

    # Check consistency within the node pool
    if consistent:
        print(f"The service on {pool} is deterministic: All responses are consistent.")
    else:
        print(f"The service on {pool} is not deterministic: Some responses differ.")

    # Update the overall consistency status
    overall_consistent = overall_consistent and consistent

# Compare results across different node pools
print("\nComparing responses across different node pools:")
cross_pool_consistent = True

# Using the first response from each pool to compare against others
pool_responses = list(first_responses.values())
for i in range(1, len(pool_responses)):
    if pool_responses[i] != pool_responses[0]:
        cross_pool_consistent = False
        print(f"Different response detected between {list(first_responses.keys())[0]} and {list(first_responses.keys())[i]}.")

# Final determinism assessment
if overall_consistent and cross_pool_consistent:
    print("The service is fully deterministic across all node pools and instance types.")
elif not overall_consistent:
    print("The service is not internally consistent within some node pools.")
else:
    print("The service behaves inconsistently across different node pools.")
