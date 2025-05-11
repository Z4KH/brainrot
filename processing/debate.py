"""
This file is used to run the debate.
"""

from processing.debate_agent import DebateAgent
from prompts import DEBATE_ROUND_PROMPT

MAX_ROUNDS = 3

class Debate:
    """
    This class is used to run the debate.
    """
    
    def __init__(self, agents: list[DebateAgent]):
        """
        Initialize the Debate.
        """
        self.agents = agents
        
    def run(self):
        """
        Run the debate.
        """
        prev_round_responses = []
        for agent in self.agents:
            prev_round_responses.append(f'{agent.agent_name}:\n{agent.opening_statement}\n\n')
        for round in range(MAX_ROUNDS):
            print(f'DEBATE ROUND {round + 1}')
            prompt = DEBATE_ROUND_PROMPT.format(round_number=round + 1, 
                                                prev_round_responses='\n\n'.join(prev_round_responses))
            prev_round_responses = []
            for agent in self.agents:
                print(f'\t{agent.agent_name} is thinking...')
                response = agent.generate_debate_response(prompt)
                prev_round_responses.append(f'{agent.agent_name}:\n{response}\n\n')
    
    
    
    
