import os
import requests
import subprocess

LEADER_URL = os.getenv('LEADER_URL', 'http://localhost:8000')

def register_follower():
    """
    Sends a request to the leader to register the follower and get a follower ID.
    """
    try:
        response = requests.post(f"{LEADER_URL}/assign_follower_id")
        if response.status_code == 200:
            follower_id = response.json().get("follower_id")
            print(f"Assigned Follower ID: {follower_id}")
            return follower_id
        else:
            print(f"Failed to register with the leader. Status Code: {response.status_code}")
            raise Exception("Follower registration failed")
    except Exception as e:
        print(f"Error connecting to the leader: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        follower_id = register_follower()
        os.environ['FOLLOWER_ID'] = follower_id
        subprocess.run(["uvicorn", "follower:app", "--host", "0.0.0.0", "--port", "8001"])
    except Exception as e:
        print(f"Failed to start follower: {e}")
        exit(1)
