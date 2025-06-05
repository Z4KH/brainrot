"""
This file contains utility functions for the debate.
"""
from debate.head_agent import HeadAgent
from debate.cluster import Cluster
from reasoning.llm import LLM
from prompts import CATEGORY_GENERATION_PROMPT

def categorize_data(data: list[dict[str, str]], llm: LLM) -> dict[str, list[str]]:
        """
        Categorize data into named groups. Returns a dictionary like:
        {"social": [...], "market": [...], "technical": [...]}
        """
        categories: dict[str, list[str]] = {}
        
        for entry in data:
            # Get category for this entry, passing existing categories
            category = get_category(entry, categories, llm)
            
            entry_tokens = estimate_tokens(entry)
            
            # Initialize category if it doesn't exist
            if category not in categories:
                categories[category] = []

            # Add entry to category
            categories[category].append(entry)
        
        return categories
    
def get_category(entry: str, existing_categories: dict[str, list[str]], llm: LLM) -> str:
        """Use LLM to determine the category for a data entry.
        
        Args:
            entry (str): The data entry string in format "Source: ... | ... | reliability: ...\nContent: ..."
            existing_categories (Dict[str, List[str]]): Existing categories and their contents
            llm (LLM): The LLM to use for categorization
            
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
        
        # Split entry into source and content
        parts = entry.split("\nContent: ")
        if len(parts) != 2:
            raise ValueError(f"Invalid entry format: {entry}")
        
        entry_source = parts[0].replace("Source: ", "")
        entry_content = parts[1]
        
        prompt = CATEGORY_GENERATION_PROMPT.format(
            source=entry_source,
            content=entry_content,
            existing_categories=categories_str
        )

        category = llm.generate(LLM.format_messages(prompt)).strip()
        return category
    
def estimate_tokens(text: str) -> int:
        """Estimate the number of tokens in a text string."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    

def cluster_agents(agents: list[HeadAgent]) -> list[Cluster]:
        """
        Cluster head agents based on differences in perspective.
        """
        clusters = []
        for agent in agents: 
            clusters.append(agent.cluster_debate_history)
        return clusters
        
        
        
       
        