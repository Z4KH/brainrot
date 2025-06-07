"""
This file contains utility functions for the debate.
"""
from debate.debate_agent import DebateAgent
from debate.cluster import Cluster
from reasoning.llm import LLM
from prompts import Prompts

def categorize_data(data: list[dict[str, str]], prompts: Prompts, llm: LLM) -> dict[str, list[str]]:
    """
    Categorize data into named groups. Returns a dictionary like:
    {"social": [...], "market": [...], "technical": [...]}
    
    :param data: The data to categorize.
    :param prompts: The prompts class to use for the category generation.
    :param llm: The LLM to use for the category generation.
    :return: A dictionary of categories and their corresponding data entries.
    """
    categories: dict[str, list[str]] = {}
    
    for entry in data:
        # Get category for this entry, passing existing categories
        category = get_category(entry, categories, prompts, llm)
        
        # Initialize category if it doesn't exist
        if category not in categories:
            categories[category] = []

        # Add entry to category
        categories[category].append(entry)
    
    return categories
    
def get_category(entry: str, existing_categories: dict[str, list[str]], prompts: Prompts, llm: LLM) -> str:
    """
    Determine the category for a data entry.
    
    :param entry: The entry to categorize.
    :param existing_categories: The existing categories.
    :param prompts: The prompts class to use for the category generation.
    :param llm: The LLM to use for the category generation.
    :return: The category for the entry.
    """
    prompt = prompts.format_category_generation_prompt(entry, existing_categories)
    return prompts.parse_category_generation_output(llm.generate(LLM.format_messages(prompt)), 
                                                    existing_categories)
    
def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string."""
    # Rough estimation: 1 token ≈ 4 characters for English text
    return len(text) // 4
    

def split_data_by_token_count(data: list[dict[str, str]], category: str, token_count: int) -> list[list[dict[str, str]]]:
    """Split data into chunks of a given token count."""
    chunks = []
    current_chunk = []
    current_chunk_tokens = 0
    for entry in data:
        entry_tokens = estimate_tokens(entry['data'])
        if current_chunk_tokens + entry_tokens > token_count:
            chunks.append(current_chunk)
            current_chunk = []
            current_chunk_tokens = 0
        current_chunk.append(entry)
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
        
        
       
        