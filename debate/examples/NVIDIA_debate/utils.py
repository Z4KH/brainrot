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
        alpha = 0.4  # Justification weight
        beta = 0.6   # Directional confidence alignment weight

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
    
    # Test case 1: Original format
    example1 = """
    Justification: My initial assessment (Round 0) highlighted a major hedge fund increasing its NVDA position by 20% (Substack, low reliability) and generally bullish institutional sentiment (Wall Street Journal, low reliability).  Rounds 1 and 2 introduced substantial conflicting information.  While several agents highlight positive short-term momentum (strong Q4 revenue, new AI chip architecture, new partnerships),  `REGULATION_Agent_0` consistently presents a strong counterargument: potential regulatory scrutiny from high-reliability sources (Barron's and Financial Times). This credible risk of negative regulatory impact outweighs the less reliable positive signals.  The numerous "Buy" recommendations often rely on medium-to-low reliability sources and lack detailed short-term price impact analysis. The consensus has shifted towards "Wait" in Rounds 1 and 2, largely due to the weight given to the high-reliability regulatory concerns.  Therefore, a cautious "Wait" position remains justified.  The upcoming earnings announcement (EARNINGS_ANNOUNCEMENT_Agent_0) adds further uncertainty, reinforcing a neutral stance.

    Position:  Wait

    Asset:  NVIDIA

    Projected Percentage Change:  
    +/-1.0%

    Time Horizon:  
    24 hours

    Confidence:  
    0.55
    """

    # Test case 2: Same-line format
    example2 = """
    Justification: NVDA is a terrible company.
    Position: Sell
    Asset: NVIDIA
    Projected Percentage Change: -4.2%
    Time Horizon: 24 hours
    Confidence: 0.92
    """

    # Test case 3: Mixed format with varying spacing
    example3 = """
    Justification:Some analysis here
    Position:  Buy
    Asset:NVIDIA
    Projected Percentage Change: +2.5%
    Time Horizon:48 hours
    Confidence:0.75
    """

    print("Test 1 (Original format):")
    print(utils.parse_agent_output(example1))
    print("\nTest 2 (Same-line format):")
    print(utils.parse_agent_output(example2))
    print("\nTest 3 (Mixed format):")
    print(utils.parse_agent_output(example3))
    
    # test get_similarity
    second_example = """
    Justification:  
    NVDA is a terrible company.

    Position:  
    Sell

    Asset:  
    NVIDIA

    Projected Percentage Change:  
    -4.2%
    
    Time Horizon:  
    24 hours

    Confidence:  
    0.92
    """
    
    print(utils.get_similarity(example1, second_example))
