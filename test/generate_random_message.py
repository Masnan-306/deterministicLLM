import os
import random

# A list of common "rainbow" words for constructing meaningful sentences
rainbow_words = [
    "amazing", "beautiful", "bright", "calm", "colorful", "dream", "energy", "fantastic", 
    "glow", "happy", "harmony", "joy", "light", "magic", "peace", "rainbow", "serene", 
    "shine", "smile", "sparkle", "vibrant", "wonder", "zen"
]

def generate_random_message(min_words=3, max_words=8):
    """Generate a random message using rainbow words."""
    num_words = random.randint(min_words, max_words)
    message = ' '.join(random.choices(rainbow_words, k=num_words))
    return message.capitalize() + "."

def generate_input_messages(file_path, num_messages=100):
    """Generate random input messages using rainbow words and save them to a file."""
    with open(file_path, 'w') as file:
        for _ in range(num_messages):
            message = generate_random_message()
            file.write(message + '\n')
    print(f"{num_messages} input messages saved to {file_path}")

if __name__ == "__main__":
    # Specify the file path for the input messages
    output_file = os.path.join(os.path.dirname(__file__), 'input_messages.txt')
    # Generate the input messages
    generate_input_messages(output_file)
