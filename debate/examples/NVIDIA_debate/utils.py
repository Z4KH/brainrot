"""
This file contains a utils class for the debate.
This class is passed to the debate class.
"""

import re
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

class Utils:
    """
    This class contains utility functions for the debate.
    """
    
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        
    def embed(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return F.normalize(embeddings, p=2, dim=1)

        def cosine_similarity(self, a, b):
            emb1 = self.embed(a)
            emb2 = self.embed(b)
            return F.cosine_similarity(emb1, emb2).item()

    
    def get_similarity(self, agent1_output: str, agent2_output: str) -> float:
        """
        Computes similarity between two agents by combining:
        - Cosine similarity of justifications
        - Direction-aware confidence alignment
        - Position match (optional bonus term)

        Returns a float in [0, 1].
        """
        alpha = 0.25  # Justification weight
        beta = 0.75   # Directional confidence alignment weight

        # Parse outputs
        parsed1 = self.parse_agent_output(agent1_output)
        parsed2 = self.parse_agent_output(agent2_output)

        # 1. Justification cosine similarity
        emb1 = self.embed(parsed1.get("justification", ""))
        emb2 = self.embed(parsed2.get("justification", ""))
        justification_sim = F.cosine_similarity(emb1, emb2).item()

        # 2. Directional signed confidence
        def get_signed_confidence(parsed):
            position = parsed.get("position", "").strip().lower()
            confidence = float(parsed.get("confidence", 0.0))
            if position == "buy":
                return confidence
            elif position == "short":
                return -confidence
            else:  # wait, unknown, etc.
                return 0.0

        signed_conf1 = get_signed_confidence(parsed1)
        signed_conf2 = get_signed_confidence(parsed2)

        # Max possible distance is 2 (e.g., +1 vs -1)
        directional_conf_sim = 1.0 - abs(signed_conf1 - signed_conf2) / 2.0

        # Final weighted score
        similarity = alpha * justification_sim + beta * directional_conf_sim
        return similarity

    
    def parse_agent_output(self, raw_output: str) -> dict:
        """
        Parses a structured agent output string into a dictionary.

        Args:
            raw_output (str): Raw multiline string from the agent.

        Returns:
            dict: Parsed output with keys:
                - justification (str)
                - position (str)
                - asset (str)
                - projected_change (float)
                - time_horizon (float) in hours
                - confidence (float) in [0, 1]
        """
        # Define possible keys
        keys = ["justification:", "position:", "asset:", "projected percentage change:", "time horizon:", "confidence:"]
        pattern = "|".join(map(re.escape, keys))

        # Split the text while keeping the keys
        parts = re.split(f"({pattern})", raw_output.lower())

        result = {}
        key = None
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part in keys:
                key = part.rstrip(":")
            elif key:
                # Collect multiline value until the next key or end
                result[key] = part
                key = None

        return result




if __name__ == "__main__":
    utils = Utils()
    
    example1 = """
Justification:  NVIDIA's Q4 revenue of $22.1 billion, a 265% year-over-year increase, and particularly the strong data center revenue of $18.4 billion driven by AI infrastructure demand, suggests significant positive momentum.  Furthermore, multiple sources report retail volume spikes following an unexpected earnings beat. While the reliability of some sources is low or medium, the high-reliability Bloomberg report strongly supports a bullish short-term outlook.

    Position:  
    Short

    Asset:  
    NVIDIA

    Projected Percentage Change:  
    +5.0%

    Time Horizon:  
    24 hours

    Confidence:  
    1
    """
    
    example2 = """
Justification:  NVIDIA's Q4 revenue surged 265% YoY to $22.1 billion, with data center revenue reaching $18.4 billion driven by AI infrastructure demand.  This massive growth, confirmed by multiple high-reliability sources (Bloomberg, Reuters, Wall Street Journal), points to a strong current market position and significant TAM expansion potential in the AI sector.  The announcement of a new AI chip architecture with 2x performance improvement (CNBC) further solidifies their technological leadership and competitive advantage.  Analyst consensus points to a price target of $1,100 (Seeking Alpha), suggesting significant upside potential. While competition exists (MarketWatch), the current data overwhelmingly demonstrates exceptional near-term growth.  High institutional buying (Investor's Business Daily) coupled with the expansion of manufacturing partnerships (Financial Times) suggests the company can meet the current, extraordinarily high demand.  Even concerns about high valuation (multiple sources) are outweighed by the extraordinary financial results and future growth potential in what CEO Huang calls "the new industrial revolution."

    Position:  
    Buy

    Asset:  
    NVIDIA

    Projected Percentage Change:  
    +5.0%

    Time Horizon:  
    24 hours

    Confidence:  
    1
    """
    
    print(utils.get_similarity(example1, example2))
