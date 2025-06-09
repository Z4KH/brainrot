"""
This file contains the code for a Debate Agent.
"""

from reasoning.llm import LLM
from enum import Enum
import re
import json


class DebateAgent:
    """
    A Debate Agent is a base agent that participates in a debate.
    """
    
    class Role(Enum):
        """
        The role of the agent in the debate.
        """
        LEAF = "leaf" # Initial dynamic agent with limited data
        HEAD = "head" # Agent that represents a cluster
        STATIC = "static" # Agent with static personality and all data
        FINAL = "final" # Final decision agent that represents the full debate

    def __init__(self, agent_name: str, category: str, data: list[dict], system_prompt: str, llm: LLM,
                 role: Role=Role.LEAF, represented_agents: list=[], represented_debate_rounds: list[dict]=[]):
        self.agent_name = agent_name
        self.category = category
        self.data = data
        self.system_prompt = system_prompt
        self.llm = llm
        self.role = role
        self.represented_agents = represented_agents
        self.represented_debate_rounds = represented_debate_rounds
        
    def initialize(self, opening_prompt: str):
        """
        Initialize the agent with an opening statement.
        """
        messages = self.llm.format_messages_with_system_prompt(self.system_prompt, opening_prompt)
        self.opening_statement = self.llm.generate(messages)
        
    def generate_debate_response(self, user_prompt: str):
        """
        Generate a debate response.
        """
        messages = self.llm.format_messages_with_system_prompt(self.system_prompt, user_prompt)
        return self.llm.generate(messages)


if __name__ == "__main__":
    # Test LeafAgent functionality
    # Create data
    print("Test Debate Agent leaf role functionality")
    from test.test import leaf_system_prompt, test_data, example_debate, leaf_user_debate_round_prompt, leaf_user_opening_prompt
    
    # Add category to each entry
    for entry in test_data:
        entry['category'] = 'News'
    
    # Create system prompt(data)
    system_prompt = leaf_system_prompt.format(agent_name='NVIDIA_News_Agent', category_name='News', data=json.dumps(test_data, indent=2))
    
    # Test opening statement generation
    llm = LLM()
    agent = DebateAgent(agent_name='NVIDIA_News_Agent', category='News', data=test_data, system_prompt=system_prompt, llm=llm)
    agent.initialize(leaf_user_opening_prompt)
    print("\n\nOpening Statement:")
    print(agent.opening_statement)
    
    # Test debate response generation
    # print("\n\nDebate Response:")
    # user_prompt = leaf_user_debate_round_prompt.format(debate_history=example_debate, round_number=2)
    # print(agent.generate_debate_response(user_prompt))

# Test HeadAgent functionality
    pass