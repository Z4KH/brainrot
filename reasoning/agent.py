"""
This file contains the code for an Agent.
"""

from reasoning.llm import LLM

class Agent:
    """
    This class is used to create an agent that can be used to generate responses using the LLM.
    The agent has a system prompt that is used to set the context for the LLM and a conversation history.
    """

    def __init__(self, system_prompt: str):
        """
        Initialize the Agent.

        Args:
            system_prompt (str): The system prompt for the LLM.
        """
        self.conversation = []
        # Initialize with a system message to set context
        self.conversation.append({
            "role": "system",
            "content": system_prompt
        })
        self.llm = LLM()


    def generate_response(self, prompt):
        """
        Generate a response using the LLM.
        
        Args:
            prompt (str): The user's input prompt
            
        Returns:
            str: The LLM's response
        """
        # Add user message to conversation history
        self.conversation.append({
            "role": "user",
            "content": prompt
        })
        
        # Get response from the model using full conversation history
        response = self.llm.generate(self.conversation)
        
        # Add assistant's response to conversation history
        self.conversation.append({
            "role": "assistant",
            "content": response
        })
        
        return response

    def clear_conversation(self):
        """
        Clear the conversation history while maintaining the system message.
        """
        system_message = self.conversation[0]
        self.conversation = [system_message]


if __name__ == "__main__":
    agent = Agent("Predict whether to buy, wait, or sell a security based on the given data. IMPORTANT: Respond with only 'buy', 'wait', or 'sell' and a brief explanation based on the past data.")
    print(agent.generate_response("Data: Italianrot memecoin price is $1,000,000. Should I buy, wait, or sell?"))
    print(agent.generate_response("Data: Italianrot memecoin price is now $1,000. Should I buy, wait, or sell?"))
