"""
This file contains the code for the information transfer layer of the system.
This layer segments the filtered data into different categories, creates agents for each category,
sets up the debate hierarchy, and passes the data to the agents.

Here is an example of the data:
data_entries = [
    {
        "source": "Reddit | 2025-05-09T13:40Z | reliability: medium",
        "data": "GME is going to explode today because..."
    },
    {
        "source": "Reuters | 2025-05-09T12:10Z | reliability: high",
        "data": "GameStop quarterly earnings beat expectations..."
    },
    ...
]
"""

from reasoning.agent import Agent
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
        self.agents = []
        self.llm = LLM()
        self.data = data

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
        

if __name__ == "__main__":
    # Sample test data
    test_data = [
        {
            "source": "Reddit | 2025-05-09T13:40Z | reliability: medium",
            "data": "GME is going to explode today because of the massive short interest and upcoming earnings call!"
        },
        {
            "source": "Reuters | 2025-05-09T12:10Z | reliability: high",
            "data": "GameStop quarterly earnings beat expectations with $1.2B in revenue, up 15% YoY"
        },
        {
            "source": "Twitter | 2025-05-09T14:20Z | reliability: low",
            "data": "Just bought 100 shares of $GME at $45.50, this is going to the moon!"
        },
        {
            "source": "Bloomberg | 2025-05-09T11:30Z | reliability: high",
            "data": "GameStop announces new partnership with major gaming studio for exclusive NFT marketplace"
        },
        {
            "source": "Reddit | 2025-05-09T15:00Z | reliability: medium",
            "data": "Technical analysis shows GME forming a bullish pennant pattern, breakout expected soon"
        }
    ]

    # Create InformationTransfer instance
    it = InformationTransfer(test_data)
    
    # Test clustering
    print("\nTesting InformationTransfer.cluster_data()...")
    print("-" * 50)
    
    categories = it.cluster_data()
    
    # Print results
    print("\nCategorized Data:")
    print("-" * 50)
    for category, entries in categories.items():
        print(f"\nCategory: {category}")
        print("-" * 30)
        for entry in entries:
            print(entry)
            print("-" * 20)
        


