import random
import os

# Define templates
templates = {
    "general_questions": [
        "What is the {thing}?",
        "How does {process} work?",
        "Who is {person}?",
        "Why is {event} important?",
        "When was {event}?"
    ],
    "personal_requests": [
        "Can you help me with {task}?",
        "Give me advice on {topic}.",
        "What's the best way to {goal}?",
        "How can I improve my {skill}?",
        "I need tips on {issue}."
    ],
    "technical_queries": [
        "How do I solve {problem} in {language}?",
        "Explain {concept} in {field}.",
        "What is the {tool} used for?",
        "How can I optimize {code}?",
        "What is the difference between {term1} and {term2}?"
    ],
    "creative_prompts": [
        "Write a short story about {subject}.",
        "Imagine a world where {scenario}.",
        "Describe a {object} in detail.",
        "Create a dialogue between {characters}.",
        "Write a poem about {theme}."
    ],
    "casual_conversation": [
        "How are you today?",
        "What's your favorite {thing}?",
        "Tell me a joke.",
        "Do you have any fun facts about {topic}?",
        "What's your opinion on {subject}?"
    ]
}

# Define word lists to fill in the templates
fillers = {
    "thing": ["internet", "weather", "space", "blockchain", "AI"],
    "process": ["photosynthesis", "machine learning", "car engine", "baking bread"],
    "person": ["Albert Einstein", "Steve Jobs", "Elon Musk", "Marie Curie"],
    "event": ["World War II", "moon landing", "industrial revolution"],
    "task": ["losing weight", "learning to code", "time management"],
    "topic": ["public speaking", "personal finance", "mental health"],
    "goal": ["run a marathon", "learn guitar", "save money"],
    "skill": ["cooking", "communication", "leadership"],
    "issue": ["stress", "lack of motivation", "procrastination"],
    "problem": ["NullPointerException", "memory leak", "syntax error"],
    "language": ["Python", "Java", "JavaScript", "C++"],
    "concept": ["recursion", "hashing", "concurrency"],
    "field": ["computer science", "physics", "economics"],
    "tool": ["Git", "Docker", "TensorFlow"],
    "code": ["this algorithm", "this script", "this loop"],
    "term1": ["OOP", "functional programming"],
    "term2": ["inheritance", "composition"],
    "subject": ["adventure", "friendship", "mystery"],
    "scenario": ["humans could fly", "robots ruled the world"],
    "object": ["antique clock", "old ship", "vintage car"],
    "characters": ["a detective and a thief", "a wizard and a dragon"],
    "theme": ["love", "loss", "nature"],
    "topic": ["space", "dinosaurs", "history"],
    "subject": ["technology", "sports", "music"],
}

# Generate random prompts
def generate_random_prompt(category):
    template = random.choice(templates[category])
    prompt = template.format(**{key: random.choice(value) for key, value in fillers.items() if "{" + key + "}" in template})
    return prompt

def generate_input_messages(file_path, num_messages=100):
    """Generate random input messages using rainbow words and save them to a file."""
    with open(file_path, 'w') as file:
        for category in templates:
            messages = set()
            for i in range(100):
                messages.add(generate_random_prompt(category))
            for message in set(messages):
                file.write(message + '\n')
    print(f"{num_messages} input messages saved to {file_path}")

if __name__ == "__main__":
    # Specify the file path for the input messages
    output_file = os.path.join(os.path.dirname(__file__), 'input_messages.txt')
    # Generate the input messages
    generate_input_messages(output_file)
