"""
This file contains the top level debate class.
"""

from debate.cluster import Cluster
from debate.debate_agent import DebateAgent
from debate.data_utils import categorize_data, split_data_by_token_count

MAX_TOKEN_COUNT = 1000

class Debate:
    """
    This class represents a debate between multiple agents.
    """
    
    def __init__(self, debate_name: str, data: list[dict], prompts, util, llm):
        """
        Initialize the Debate class with data, prompts, utility functions, and an LLM.
        """
        self.debate_name = debate_name
        self.data = data
        self.prompts = prompts
        self.util = util
        self.llm = llm
        self.layers = []

    def initialize(self, max_token_count=MAX_TOKEN_COUNT):
        """
        Initialize the debate by creating a the first layer of debate agents.
        
        :param max_token_count: The maximum number of tokens allowed for a single debate agent.
        """
        # Categorize data
        categories = categorize_data(self.data, self.prompts, self.llm)
        # Form clusters
        for category in categories:
            cluster_name = f"{category}_Cluster"
            # Split data within each category by token count
            data_chunks = split_data_by_token_count(self.data, category, token_count=max_token_count)
            # Create debate agents for each chunk
            debate_agents = []
            for i, chunk in enumerate(data_chunks):
                agent_name = f"{category}_Agent_{i}"
                system_prompt = self.prompts.format_leaf_agent_system_prompt(agent_name=agent_name, category=category, data=chunk)
                agent = DebateAgent(agent_name=agent_name, category=category, data=chunk,
                                                 system_prompt=system_prompt, llm=self.llm)
                agent.initialize(opening_prompt=self.prompts.format_leaf_agent_opening_prompt())
                debate_agents.append(agent)

            # Create cluster
            cluster = Cluster(cluster_name, debate_agents, self.prompts)
            self.layers.append([cluster])
    
    def run_debate(self, num_rounds, num_layers):
        """
        Run the debate for a given number of rounds and layers.
        
        :param num_rounds: The number of rounds to run the debate within each cluster.
        :param num_layers: The number of reclusterization rounds to run.
        """
        pass

        
        

if __name__ == "__main__":
    # Create data
    from prompts import Prompts
    from reasoning.llm import LLM
    from test.test import test_data
    prompts = Prompts()
    llm = LLM()
    debate = Debate(debate_name="NVIDIA", data=test_data, prompts=prompts, util=None, llm=llm)
    debate.initialize()
    for layer in debate.layers:
        for cluster in layer:
            print(f'{cluster.cluster_name} with {len(cluster.debate_agents)} agents:')
            for agent in cluster.debate_agents:
                print(agent.agent_name)
                print(agent.opening_statement)
                print("--------------------------------")
            print("########################")
    # debate.run_debate(rounds=3, layers=2)
    # get & output final position from final head agent
        
        
