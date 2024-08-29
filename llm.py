from llama_cpp import Llama

# Load the model
llm = Llama.from_pretrained(
    repo_id="TheBloke/Tinyllama-2-1b-miniguanaco-GGUF",
    filename="tinyllama-2-1b-miniguanaco.Q2_K.gguf",
)

# Function to generate responses
def chat_with_model(message):
    llm.reset()
    
    # Initialize conversation history with a system message
    conversation_history = [
        {"role": "system", "content": "You are an AI assistant that helps users with information and conversations. Respond clearly and concisely."},
        {"role": "user", "content": message}
    ]
    
    response = llm.create_chat_completion(
        messages=conversation_history,
        temperature=0,
        seed=123
    )
    
    # Clean up the response by removing unwanted tokens
    output = response["choices"][0]["message"]["content"]
    return output

# Main loop to interact with the model
def main():
    print("Welcome to the Llama Chat! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Generate the model's response based on the conversation history
        response = chat_with_model(user_input)

        print(f"Llama: {response}")

if __name__ == "__main__":
    main()
