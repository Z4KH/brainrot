"""
This file contains the top level debate class.
"""

from debate.cluster import Cluster
from debate.debate_agent import DebateAgent
from debate.static_debate_agent import StaticDebateAgent
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
        self.layers = [[]]
        self.initialized = False
        self.final_position = None

    def initialize(self, max_token_count=MAX_TOKEN_COUNT, num_static_agents=0):
        """
        Initialize the debate by creating a the first layer of debate agents.
        
        :param max_token_count: The maximum number of tokens allowed for a single debate agent.
        :param num_static_agents: Number of static persona agents to include (0-5).
        """
        # Categorize data
        categories = categorize_data(self.data, self.prompts, self.llm)
        
        # Form clusters from dynamic categorized agents
        for category in categories:
            cluster_name = f"{category}_Cluster"
            # Split data within each category by token count
            data_chunks = split_data_by_token_count(categories[category], category, token_count=max_token_count)
            # Create debate agents for each chunk
            debate_agents = []
            for i, chunk in enumerate(data_chunks):
                agent_name = f"{category}_Agent_{i}"
                system_prompt = self.prompts.format_leaf_agent_system_prompt(agent_name=agent_name, category=category, data=chunk)
                agent = DebateAgent(agent_name=agent_name, category=category, data=chunk,
                                                 system_prompt=system_prompt, llm=self.llm)
                agent.initialize(opening_prompt=self.prompts.format_leaf_agent_opening_prompt())
                debate_agents.append(agent)
            # Create the debate cluster for this category
            cluster = Cluster(cluster_name, debate_agents, self.prompts)
            self.layers[0].append(cluster)
        
        # Create static agents if requested
        if num_static_agents > 0 and self.layers[0]:
            static_agents = StaticDebateAgent.create_static_agents(num_static_agents, self.data, self.llm)
            for agent in static_agents:
                agent.initialize(opening_prompt=self.prompts.format_leaf_agent_opening_prompt())
        
            # Distribute static agents across existing clusters in round-robin fashion
            # All clusters will have at least one dynamic agent at this point
            for i, static_agent in enumerate(static_agents):
                target_cluster_idx = i % len(self.layers[0])
                self.layers[0][target_cluster_idx].add_agent(static_agent)
        
        self.initialized = True
    
    def run_debate(self, num_rounds, num_hidden_layers):
        """
        Run the debate for a given number of rounds and layers.
        Note: num_layers is the maximum number of reclusterization rounds to run.
        This does not include the initial layer with categorical clusters or 
        the final layer with the final head agent.
        
        :param num_rounds: The number of rounds to run the debate within each cluster.
        :param num_hidden_layers: The maximum number of reclusterization rounds to run.
        :return: The final position of the final head agent.
        """
        if not self.initialized:
            raise ValueError("Debate must be initialized before being run.")
        c0 = len(self.layers[0]) # Number of clusters in the first layer
        cluster_counts = self.compute_cluster_counts(c0, 1, num_hidden_layers)
        for i in range(num_hidden_layers):
            head_agents = []
            for cluster in self.layers[i]:
                cluster.debate(num_rounds)
                head_agents.append(cluster.initialize_head_agent())
            if cluster_counts[i] > 1:
                c_next = cluster_counts[i+1]
                self.layers.append(self.recluster(head_agents, c_next, i+1))
            else: break
        # Final layer will have only one cluster
        final_cluster = self.layers[-1][0]
        final_cluster.debate(num_rounds)
        final_head_agent = final_cluster.initialize_head_agent(final_agent=True)
        self.layers.append([Cluster(f'{self.debate_name}_FinalCluster', [final_head_agent], self.prompts)])
        self.final_position = self.util.parse_agent_output(final_head_agent.opening_statement)
        return self.final_position
        
    
    def recluster(self, head_agents, c_next, layer_index):
        """
        Recluster the head agents into a new clusters
        to form the next layer.
        
        For each agent, compute the change in diversity score of the cluster
        for each cluster if the agent were to be added to that cluster.
        Add the agent to the cluster with the most positive change in diversity score.
        
        :param head_agents: The head agents to recluster.
        :param c_next: The number of clusters to form in the next layer.
        :param layer_index: The index of the current layer.
        :return: A list of the new clusters.
        """
        clusters = [Cluster(f"{self.debate_name}_Cluster{i}_Layer{layer_index}", [], self.prompts) for i in range(c_next)]
        for agent in head_agents:
            if c_next == 1:
                clusters[0].add_agent(agent)
                continue
            best_cluster = None
            best_diversity_change = -float('inf')
            for i, cluster in enumerate(clusters):
                initial_diversity = cluster.get_diversity_score(self.util)
                new_diversity = cluster.get_diversity_score(self.util, additional_agents=[agent])
                diversity_change = new_diversity - initial_diversity
                if diversity_change > best_diversity_change:
                    best_diversity_change = diversity_change
                    best_cluster = i
            clusters[best_cluster].add_agent(agent)
        return clusters

    def compute_cluster_counts(self, c0, cL, L):
        """
        Compute the number of clusters in each layer.
        Uses exponential decay: c_i = c_0 * beta^i
        beta = (cL / c0) ** (1 / L)
        
        :param c0: The number of clusters in the first layer.
        :param cL: The number of clusters in the last layer.
        :param L: The number of layers.
        :return: A list of the number of clusters in each layer.
        """
        beta = (cL / c0) ** (1 / L)
        return [max(1, int(round(c0 * (beta ** i)))) for i in range(L + 1)]
    
    def get_debate(self):
        """
        Get the debate as a string.
        
        :return: A string representation of the debate.
        """
        if not self.final_position:
            raise ValueError("Debate must be run before getting the debate.")
        debate = f"DEBATE: {self.debate_name}\n"
        debate += f"Final Position: {self.final_position}\n"
        debate += "LAYERS:\n"
        for i, layer in enumerate(self.layers):
            debate += f'========== LAYER {i} ==========\n'
            cluster_debate = ""
            for cluster in layer:
                cluster_debate += f'{cluster.cluster_name} with {len(cluster.debate_agents)} agents:\n'
                cluster_debate += cluster.format_debate()
                cluster_debate += "########################\n"
            debate += self.indent_text(cluster_debate, prefix='    ')
        return debate
    
    def indent_text(self, text, prefix='    '):
        """
        Indent the text with a given prefix.
        """
        return ''.join(prefix + line if line.strip() else line for line in text.splitlines(True))
