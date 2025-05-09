"""
This file contains the code for the information transfer layer of the system.
This layer segments the filtered data into different categories, creates agents for each category,
sets up the debate hierarchy, and passes the data to the agents.
"""

from reasoning.agent import Agent

class InformationTransfer:
    """
    This class is used to transfer the information to the agents.
    """

    def __init__(self, data: dict[str, list[dict]]):
        """
        Initialize the InformationTransfer class.

        Args:
            data (dict[str, list[dict]]): The data to be transferred to the agents.
        """
        self.agents = []
        self.debate_hierarchy = []

