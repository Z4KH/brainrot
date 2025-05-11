"""
This file contains the code for an Agent.

TODO:
- add a method to transfer data to the agent
- fix parsing response to add to conversation/prompt
"""

from reasoning.llm import LLM
from prompts import DEBATE_AGENT_SYSTEM_PROMPT, TRANSFER_DATA_PROMPT

import re


class DebateAgent:
    """
    This class is used to create an agent that can be used to generate responses using the LLM.
    The agent has a system prompt that is used to set the context for the LLM and a conversation history.
    """

    def __init__(self, category: str, entries: list[str]):
        """
        Initialize the DebateAgent.

        Args:
            system_prompt (str): The system prompt for the LLM.
        """
        self.agent_name = f'{category} Expert Agent'
        self.entries = entries
        self.category = category
        self.conversation = []
        self.system_prompt = self._build_system_prompt()
        self.llm = LLM()
        self.conversation.append({
            "role": "system",
            "content": self.system_prompt
        })
        self.round_number = 0


    def generate_debate_response(self, prompt):
        """
        Generate a response using the LLM.
        TODO: make prompt and handle converssation history smarter
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
        
        
    def _build_system_prompt(self) -> str:
        """
        Build a system prompt for the agent.
        """
        system_prompt = DEBATE_AGENT_SYSTEM_PROMPT.format(
            agent_name=self.agent_name,
            category_name=self.category
        )
        return system_prompt
    
    
    def _format_data(self) -> str:
        """
        Format the data entries for LLM input using structured, agent-friendly format.
        Expected each entry to be a dict with keys:
        - 'source': str
        - 'timestamp': str (ISO format)
        - 'reliability': str
        - 'data': str
        """
        import re

    def _format_data(self) -> str:
        """
        Reformat raw string entries into clean, structured format for LLM input.
        Each entry is a string like:
        "Source: Reddit | 2025-05-09T13:40Z | reliability: medium\nContent: ..."
        """
        formatted_entries = []

        for i, raw_entry in enumerate(self.entries, start=1):
            lines = raw_entry.strip().split('\n')
            
            # Default values
            source = "Unknown"
            timestamp = "Unknown"
            reliability = "Unknown"
            content = ""

            for line in lines:
                if line.startswith("Source:"):
                    # Split the source line using pipe-delimited fields
                    parts = line.replace("Source:", "").strip().split("|")
                    if len(parts) >= 1:
                        source = parts[0].strip()
                    if len(parts) >= 2:
                        timestamp = parts[1].strip()
                    if len(parts) >= 3:
                        reliability_match = re.search(r"reliability:\s*(\w+)", parts[2], re.IGNORECASE)
                        if reliability_match:
                            reliability = reliability_match.group(1).capitalize()
                elif line.startswith("Content:"):
                    content = line.replace("Content:", "").strip()

            formatted = (
                f"[Entry {i}]\n"
                f"Source: {source}\n"
                f"Timestamp: {timestamp}\n"
                f"Reliability: {reliability}\n"
                f"Content: {content}"
            )

            formatted_entries.append(formatted)

        return "\n\n".join(formatted_entries)


    def transfer_data(self):
        """
        Transfer the data to the agent.
        """
        prompt = TRANSFER_DATA_PROMPT.format(
            data=self._format_data()
        )
        self.conversation.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.llm.generate(self.conversation)
        
        self.conversation.append({
            "role": "assistant",
            "content": response
        })
        self.opening_statement = response
        self.round_number += 1
        
        
    def output_conversation(self, filename: str = 'out.txt'):
        """
        Print the entire conversation in a nicely formatted way.
        """
        if filename:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}")
                f.write(f"\nAgent: {self.agent_name}")
                f.write(f"\n{'='*80}")
                
                for message in self.conversation:
                    f.write(f"\n{message['role'].upper()}:")
                    f.write(f"\n{'-'*40}")
                    f.write(f"{message['content']}\n")
                    f.write(f"\n{'-'*40}\n")
                    
                f.write(f"\n{'='*80}\n")