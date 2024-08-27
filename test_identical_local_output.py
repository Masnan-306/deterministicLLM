import unittest
from llm import chat_with_model

class TestChatWithModelDeterminism(unittest.TestCase):
    def test_deterministic_output(self):
        messages = [
            "hi",
            "What is the weather like today?",
            "Were is the capital of China?",
            "How do you implement a Hash Table?",
            "Thank you!"
        ]
        
        for message in messages:
            # Run the function multiple times with the same input
            output1 = chat_with_model(message)
            output2 = chat_with_model(message)
            output3 = chat_with_model(message)
            
            # Check if all outputs are the same
            self.assertEqual(output1, output2, f"The output for prompt {message} is not deterministic between run 1 and run 2.")
            self.assertEqual(output1, output3, f"The output for prompt {message} is not deterministic between run 1 and run 3.")

if __name__ == '__main__':
    unittest.main()
