"""
This file contains the code for the information transfer layer of the system.
This layer segments the filtered data into different categories, creates agents for each category,
sets up the debate hierarchy, and passes the data to the agents.
"""

from processing.debate_agent import DebateAgent
from reasoning.llm import LLM
import re
from typing import Dict, List, Tuple
from prompts import CATEGORY_GENERATION_PROMPT

MAX_TOKENS = 1000

class InformationTransfer:
    """
    This class is used to transfer the information to the agents.
    """

    def __init__(self, data: list[dict[str, str]]):
        """
        Initialize the InformationTransfer class.

        Args:
            data (list[dict[str, str]]): The data to be transferred to the agents.
                str is the source of the data, and str is the data.
        """
        self.llm = LLM()
        self.data = data
        self.categories = self.cluster_data()
        self.agents = self.create_agents()

    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text string."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def _extract_source_type(self, source: str) -> str:
        """Extract the source type from the source string."""
        if "|" in source:
            return source.split("|")[0].strip()
        return source

    def _get_category(self, entry: dict[str, str], existing_categories: Dict[str, List[str]] = None) -> str:
        """Use LLM to determine the category for a data entry.
        
        Args:
            entry (dict[str, str]): The data entry to categorize
            existing_categories (Dict[str, List[str]], optional): Existing categories and their contents
            
        Returns:
            str: The category name for the entry
        """
        # Format existing categories for the prompt
        categories_str = ""
        if existing_categories:
            for category, contents in existing_categories.items():
                categories_str += f"\n{category}:\n"
                # Show first entry as example
                if contents:
                    categories_str += f"Example: {contents[0]}\n"
        
        prompt = CATEGORY_GENERATION_PROMPT.format(
            source=entry['source'],
            content=entry['data'],
            existing_categories=categories_str
        )

        category = self.llm.generate(LLM.format_messages(prompt)).strip()
        return category

    def cluster_data(self) -> dict[str, list[str]]:
        """
        Cluster the data into different categories.
        The structure of the output is:
        {
            "category_name": "parsed data structured nicely"
        }
        Returns:
            dict[str, list[str]]: The data grouped by category.
        """
        categories: Dict[str, List[str]] = {}
        current_category_tokens: Dict[str, int] = {}
        
        for entry in self.data:
            # Get category for this entry, passing existing categories
            category = self._get_category(entry, categories)
            
            # Format the entry
            formatted_entry = f"Source: {entry['source']}\nContent: {entry['data']}\n"
            entry_tokens = self._estimate_tokens(formatted_entry)
            
            # Check if we need to create a new category due to token limit
            if category in current_category_tokens and current_category_tokens[category] + entry_tokens > MAX_TOKENS:
                # Create a new category with a suffix
                base_category = category
                suffix = 1
                while f"{base_category}_{suffix}" in categories:
                    suffix += 1
                category = f"{base_category}_{suffix}"
            
            # Initialize category if it doesn't exist
            if category not in categories:
                categories[category] = []
                current_category_tokens[category] = 0
            
            # Add entry to category
            categories[category].append(formatted_entry)
            current_category_tokens[category] += entry_tokens
        
        return categories
    
    def create_agents(self) -> list[DebateAgent]:
        """
        Create agents for each category and transfer the data to them.
        TODO: Hierachy of agents/Grouping of agents
        
        Returns:
            list[DebateAgent]: The list of agents.
        """
        agents = []
        for category, entries in self.categories.items():
            agent = DebateAgent(category, entries)
            agent.transfer_data()
            agents.append(agent)
        return agents



if __name__ == "__main__":
    # Sample test data with conflicting and noisy information
    test_data = [
        {
            "source": "Reuters | 2025-05-09T12:10Z | reliability: high",
            "data": "BREAKING: Elon Musk announces he's changing his name to 'ClownCoin' and launching a new cryptocurrency"
        },
        {
            "source": "Twitter | 2025-05-09T12:15Z | reliability: high",
            "data": "This is Elon Musk. I have NOT changed my name and I have NOT launched any cryptocurrency. Beware of scams."
        },
        {
            "source": "Reddit | 2025-05-09T13:40Z | reliability: medium",
            "data": "Just bought 1000 ClownCoin at $0.001, this is going to the moon!"
        },
        {
            "source": "Bloomberg | 2025-05-09T11:30Z | reliability: high",
            "data": "ClownCoin surges 500% after viral tweet from @elonmusk, but account appears to be fake"
        },
        {
            "source": "Twitter | 2025-05-09T14:20Z | reliability: low",
            "data": "ClownCoin is a scam! I lost all my life savings!"
        },
        {
            "source": "Reddit | 2025-05-09T15:00Z | reliability: medium",
            "data": "Technical analysis shows ClownCoin forming a bullish pennant pattern, breakout expected soon"
        },
        {
            "source": "CNBC | 2025-05-09T16:00Z | reliability: high",
            "data": "SEC launches investigation into ClownCoin after reports of market manipulation"
        },
        {
            "source": "Twitter | 2025-05-09T16:30Z | reliability: low",
            "data": "Just met @elonmusk at Tesla factory, he confirmed ClownCoin is legit!"
        },
        {
            "source": "WSJ | 2025-05-09T17:00Z | reliability: high",
            "data": "ClownCoin trading volume exceeds $1B in 24 hours, but 80% of transactions appear to be wash trading"
        },
        {
            "source": "Reddit | 2025-05-09T17:30Z | reliability: medium",
            "data": "My uncle works at Tesla and he says ClownCoin is actually a secret project by Elon"
        },
        {
            "source": "Twitter | 2025-05-09T18:00Z | reliability: high",
            "data": "This is Elon Musk. I am suing the creators of ClownCoin for using my name without permission."
        },
        {
            "source": "Reddit | 2025-05-09T18:30Z | reliability: low",
            "data": "ClownCoin devs just doxxed themselves, they're actually from North Korea!"
        }
    ]

    # Create InformationTransfer instance
    it = InformationTransfer(test_data)
        


