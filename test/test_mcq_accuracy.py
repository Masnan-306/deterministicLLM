import datasets
import requests
from tqdm import tqdm

def evaluate_service_accuracy(dataset_name: str = "TIGER-Lab/MMLU-Pro"):
    """
    Utility to evaluate the accuracy of the service on a group of inputs from the MMLU dataset.
    """
    # Load the dataset
    dataset = datasets.load_dataset(dataset_name)
    dataset = dataset["validation"]

    correct_count = 0
    total_count = 0

    # Wrap dataset with tqdm for progress bar
    for item in tqdm(dataset, desc="Evaluating", unit="question"):
        question = item["question"]
        options = item["options"]
        correct_answer = item["answer"]

        # Prepare the payload for the API
        payload = {
            "question": question,
            "options": options
        }

        # Send request to the local FastAPI service
        response = requests.post("http://localhost:80/mcq", json=payload)
        if response.status_code == 200:
            predicted_answer = response.json().get("answer")
            # print(predicted_answer, correct_answer, options)
            if predicted_answer == correct_answer:
                correct_count += 1
            total_count += 1
        else:
            print(f"Error: Received status code {response.status_code} for question: {question}")

    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    print(f"Accuracy: {accuracy:.2f}% ({correct_count}/{total_count})")

if __name__ == "__main__":
    evaluate_service_accuracy()