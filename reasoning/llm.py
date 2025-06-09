"""
This file contains the code to interact with the LLM.
"""



### TOGETHER API ###
# MODEL = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'
# URL = 'https://api.together.xyz/v1/chat/completions'
# from together import Together
# TOGETHER = True
# GROQ = False
# GEMINI = False

### GROQ API ###
# MODEL = 'meta-llama/llama-4-scout-17b-16e-instruct'
# URL = 'https://api.groq.com/openai/v1/chat/completions'
# from groq import Groq
# GROQ = True
# TOGETHER = False
# GEMINI = False

### GEMINI API ###
MODEL = 'gemini-1.5-flash'
from google.oauth2 import service_account
import google.generativeai as genai
GEMINI = True
TOGETHER = False
GROQ = False

import os
import time

class LLM:
    """
    This class is used to interact with the LLM.
    """

    def __init__(self):
        if TOGETHER:
            self.client = Together(api_key=os.getenv('TOGETHER_API_KEY'))
        elif GROQ:
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        elif GEMINI:
            # Load credentials from service account file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            creds_path = os.path.join(current_dir, 'env', 'gen-lang-client.json')
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
                
            creds = service_account.Credentials.from_service_account_file(creds_path)
            genai.configure(credentials=creds)
            self.client = genai.GenerativeModel(MODEL)
        else: 
            raise ValueError("No LLM API specified")


    def generate(self, messages: list[dict]) -> str:
        """
        This function is used to get a response from the LLM.
        """
        max_retries = 3
        for i in range(max_retries):
            try:
                if GEMINI:
                    # Convert messages to Gemini format
                    prompt = self._convert_messages_to_gemini_format(messages)
                    response = self.client.generate_content(prompt)
                    content = response.text
                else:
                    # Together and Groq use the same format
                    response = self.client.chat.completions.create(
                        model=MODEL,
                        messages=messages
                    )
                    content = response.choices[0].message.content
                break
            except Exception as e:
                print(f"Error generating response: {e}")
                if i == max_retries - 1:
                    raise e
                time.sleep(60) # Likely rate limited -- wait 60 seconds and try again
                with open("error.txt", "a") as f:
                    f.write(f"Error generating response: {e}\n")
                    f.write(f"Messages: {messages}\n")
                    f.write(f"Response: {response if 'response' in locals() else 'None'}\n")
                    f.write(f"Time: {time.time()}\n")
                    f.write(f"Model: {MODEL}\n")
                    if not GEMINI:
                        f.write(f"URL: {URL}\n")
        # Add assistant's response to conversation history
        return content
    
    def _convert_messages_to_gemini_format(self, messages: list[dict]) -> str:
        """
        Convert OpenAI-style messages to Gemini prompt format.
        """
        prompt_parts = []
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(content)
        
        return "\n\n".join(prompt_parts)
    
    def format_messages(self, prompt: str) -> list[dict]:
        """
        This function is used to format the messages for the LLM.
        """
        return [
            {"role": "user", "content": prompt}
        ]
    
    def format_messages_with_system_prompt(self, system_prompt: str, user_prompt: str) -> list[dict]:
        """
        This function is used to format the messages for the LLM with a system prompt.
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

if __name__ == "__main__":
    llm = LLM()
    print(llm.generate(llm.format_messages("What is the capital of France?")))




