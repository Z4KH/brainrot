"""
This file contains the top level debate class.
"""

from debate.cluster import Cluster
from debate.debate_agent import DebateAgent
from info_utils import categorize_data

class Debate:
    """
    This class represents a debate between multiple agents.
    """
    
    def __init__(self, data: list[dict], prompts, util, llm):
        """
        Initialize the Debate class with data, prompts, utility functions, and an LLM.
        """
        self.data = data
        self.prompts = prompts
        self.util = util
        self.llm = llm
        self.clusters = []

    def initialize(self):
        """
        Initialize the debate by categorizing data and creating clusters of debate agents.
        """
        # Create clusters based on data categories
        categories = categorize_data(self.data)
        for category in categories:
            cluster_name = f"{category}_Cluster"
            cluster_data = self.util.filter_data_by_category(self.data, category)
            system_prompt = self.prompts.format_cluster_system_prompt(cluster_name, cluster_data)
            debate_agents = [DebateAgent(agent_name=f"{category}_Agent_{i}", category=category, data=cluster_data,
                                         system_prompt=system_prompt, llm=self.llm) for i in range(3)]
            cluster = Cluster(cluster_name, debate_agents, self.prompts)
            self.clusters.append(cluster)

        # Initialize head agents for each cluster
        for cluster in self.clusters:
            cluster.initialize_head_agent()
        
        

if __name__ == "__main__":
    # Create data
    # debate = Debate(data, prompts, util, llm)
    # debate.initialize()
    # debate.run_debate(rounds=3, layers=2)
    # get & output final position from final head agent
        
        
