import requests
import csv
import json
import os

# Specify the REGION and DNS name for the configuration
REGION = "eastus"
IP_ADDRESS = "51.8.24.242"
tsv_filename = f"outputs/results_{REGION}_{IP_ADDRESS}.tsv"

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """
    Simple progress bar.
    """
    percent = f"{100 * (iteration / float(total)):.{decimals}f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def send_request(input_message):
    """Send a POST request to the FastAPI endpoint with the input message."""
    url = f"http://{IP_ADDRESS}/chat"  # Adjust to your server URL
    try:
        response = requests.post(url, json={"message": input_message})
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"

def process_input_messages(input_file, output_tsv):
    """Read input messages from a file, send requests, and save results to a TSV file."""
    with open(input_file, 'r') as infile, open(output_tsv, 'w', newline='') as tsvfile:
        reader = infile.readlines()
        writer = csv.writer(tsvfile, delimiter='\t')  # Use tab as the delimiter for TSV
        writer.writerow(['Input', 'Output'])

        for i, line in enumerate(reader):
            print_progress_bar(i + 1, len(reader))
            input_message = line.strip()
            if input_message:
                response = send_request(input_message)
                escaped_response = json.dumps(response)
                writer.writerow([input_message, escaped_response])
    
    print(f"\nResults saved to {output_tsv}")



if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(__file__), 'input_messages.txt')
    process_input_messages(input_file, tsv_filename)
