"""
This file contains the code to interact with the LLM.
"""



### TOGETHER API ###
# MODEL = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'
# URL = 'https://api.together.xyz/v1/chat/completions'
# from together import Together
# TOGETHER = True
# GROQ = False

### GROQ API ###
MODEL = 'meta-llama/llama-4-maverick-17b-128e-instruct'
URL = 'https://api.groq.com/openai/v1/chat/completions'
from groq import Groq
GROQ = True
TOGETHER = False

import os

class LLM:
    """
    This class is used to interact with the LLM.
    """

    def __init__(self):
        if TOGETHER:
            self.client = Together(api_key=os.getenv('TOGETHER_API_KEY'))
        elif GROQ:
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        else: raise ValueError("No LLM API specified")


    def generate(self, messages: list[dict]) -> str:
        """
        This function is used to get a response from the LLM.
        """
        response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
        # Add assistant's response to conversation history
        return response.choices[0].message.content
    
    
    def format_messages(prompt: str) -> list[dict]:
        """
        This function is used to format the messages for the LLM.
        """
        return [
            {"role": "user", "content": prompt}
        ]


if __name__ == "__main__":
    llm = LLM()
    print(llm.generate(LLM.format_messages("What is the capital of France?")))




