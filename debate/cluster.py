"""
This module is used to create and interface with a cluster of agents.
"""

from debate.debate_agent import DebateAgent

class Cluster:
    """
    Represents a group of DebateAgents who will internally debate.
    Tracks all round outputs and supports head agent synthesis later.
    """

    def __init__(self, cluster_name: str, debate_agents: list[DebateAgent], prompts):
        self.cluster_name = cluster_name
        self.debate_agents = debate_agents
        self.prompts = prompts
        self.debate_rounds = [{}]
        
        # Add opening statements to debate_rounds
        for agent in self.debate_agents:
            self.debate_rounds[0][agent.agent_name] = agent.opening_statement
    
    def add_agent(self, agent: DebateAgent):
        """
        Add an agent to the cluster.
        The agent will be added to the most recent round of the debate.
        
        :param agent: The agent to add to the cluster.
        """
        self.debate_agents.append(agent)
        self.debate_rounds[-1][agent.agent_name] = agent.opening_statement

    def debate(self, num_rounds: int):
        """
        Conduct a debate for a given number of rounds.
        """
        if len(self.debate_agents) == 1:
            return # No debate needed if there is only one agent
        for round_number in range(1, num_rounds + 1):
            self.debate_rounds.append({})
            for agent in self.debate_agents:
                prompt = self.prompts.format_leaf_agent_debate_prompt(round_number, self.format_debate(round_number))
                response = agent.generate_debate_response(prompt)
                self.debate_rounds[round_number][agent.agent_name] = response
                
            
    def format_debate(self, round_number: int = None):
        """
        Format the debate for printing up to a given round.
        
        :param round_number: The round number to format up to.
        :return: A string of the formatted debate.
        """
        if round_number is None:
            round_number = len(self.debate_rounds)
        formatted_debate = ""
        
        # Format each round
        for round_num, round_data in enumerate(self.debate_rounds[:round_number]):
            if round_num == 0: round_type = "Opening Statements"
            else: round_type = "Debate"
            formatted_debate += f"\n========== ROUND {round_num} ({round_type}) ==========\n"
            
            # Format each agent's statement in the round
            for agent_name, statement in round_data.items():
                formatted_debate += f"{agent_name}:\n{statement}\n\n"
                
        return formatted_debate

    def initialize_head_agent(self, final_agent: bool = False):
        """
        Initialize the head agent.
        
        :param final_agent: Whether this is the final head agent.
        :return: The head agent.
        """
        if len(self.debate_agents) == 1:
            return self.debate_agents[0] # No head agent needed if there is only one agent
        if final_agent:
            head_agent_name = 'FinalDecisionAgent'
        else:
            head_agent_name = f'{self.cluster_name}_HeadAgent'
        data = []
        represented_agent_names = []
        for agent in self.debate_agents:
            data += agent.data
            represented_agent_names.append(agent.agent_name)
        if not final_agent: 
            system_prompt = self.prompts.format_head_agent_system_prompt(
                head_agent_name, self.cluster_name, data, self.format_debate(), represented_agent_names)
            opening_prompt = self.prompts.format_head_agent_opening_prompt()
            role = 'head'
        else:
            system_prompt = self.prompts.format_final_head_agent_system_prompt(
                head_agent_name, self.cluster_name, data, self.format_debate(), represented_agent_names)
            opening_prompt = self.prompts.format_final_agent_decision_prompt()
            role = 'final'
        head_agent = DebateAgent(agent_name=head_agent_name, category=self.cluster_name, data=data, 
                                 system_prompt=system_prompt, llm=self.debate_agents[0].llm, role=role, represented_agents=self.debate_agents,
                                 represented_debate_rounds=self.debate_rounds)
        head_agent.initialize(opening_prompt)
        return head_agent
    
    def get_diversity_score(self, util, additional_agents: list[DebateAgent] = []):
        """
        Get the diversity score of the cluster based on the diversity of the opening statements.
        Diversity score is computed as (1 - average_pairwise_similarity)
        
        :param util: The utility object to use for similarity calculations.
        :param additional_agents: Additional agents to include in the diversity score calculation.
        :return: The diversity score.
        """
        agents = self.debate_agents + additional_agents
        if not agents or len(agents) == 1: return 0 # No agents to compute diversity score
        similarity_matrix = [[0 for _ in agents] for _ in agents]
        for i in range(len(agents)):
            for j in range(i+1, len(agents)):
                similarity_matrix[i][j] = util.get_similarity(agents[i].opening_statement, agents[j].opening_statement)
                similarity_matrix[j][i] = similarity_matrix[i][j]
        # Sum upper triangle off-diagonal elements
        sum_similarity = 0
        for i in range(len(agents)):
            for j in range(i+1, len(agents)):
                sum_similarity += similarity_matrix[i][j]
        average_similarity = sum_similarity / (len(agents) * (len(agents) - 1) / 2)
        return 1 - average_similarity

if __name__ == "__main__":
    # Test Cluster functionality
    # Create data
    from test.test import leaf_system_prompt, test_data, example_debate, leaf_user_debate_round_prompt, leaf_user_opening_prompt
    from reasoning.llm import LLM
    from prompts import Prompts
    from utils import Utils
    llm = LLM()
    util = Utils()
    # Create agents
    agents = []
    prompts = Prompts()
    for category in ['NVIDIA_News', 'NVIDIA_Earnings', 'NVIDIA_Earnings_Call', 'NVIDIA_Earnings_Call_Transcript']:
        agent_name = f'{category}_Agent'
        leafSystem = prompts.format_leaf_agent_system_prompt(agent_name, category, test_data)
        agent = DebateAgent(agent_name=agent_name, category=category, data=test_data, system_prompt=leafSystem, llm=llm, role='leaf')
        agents.append(agent)
    
    # Create opening statements
    for agent in agents:
        opening_prompt = prompts.format_leaf_agent_opening_prompt()
        agent.initialize(opening_prompt)
        
    # Create cluster
    cluster = Cluster(cluster_name="Cluster1", debate_agents=agents, prompts=prompts)
    cluster.debate(num_rounds=2)
    print(f"Debate complete:\n{cluster.format_debate()}\n\n")
    
    head_agent = cluster.initialize_head_agent()
    print(f"Head agent:\n{head_agent.opening_statement}\n\n")


