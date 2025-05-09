"""
This file contains the code to interact with the LLM.
"""

MODEL = 'meta-llama/Llama-Vision-Free'
URL = 'https://api.together.xyz/v1/chat/completions'

from together import Together
import os

class LLM:
    """
    This class is used to interact with the LLM.
    """

    def __init__(self):
        self.together = Together(api_key=os.getenv('TOGETHER_API_KEY'))


    def get_llm_response(self, messages: list[dict]) -> str:
        """
        This function is used to get a response from the LLM.
        """
        response = self.together.chat.completions.create(
                model=MODEL,
                messages=messages
            )
        # Add assistant's response to conversation history
        return response.choices[0].message.content






