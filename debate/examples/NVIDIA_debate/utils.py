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
            confidence = parsed.get("confidence", 0.0)
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
        output = {
            "justification": None,
            "position": None,
            "asset": None,
            "projected_change": None,
            "time_horizon": None,
            "confidence": None
        }

        # Normalize line endings
        lines = raw_output.strip().replace("\r\n", "\n").split("\n")

        # Join lines into chunks between headers
        current_key = None
        buffer = []
        mapping = {
            "justification": "justification",
            "position": "position",
            "asset": "asset",
            "projected percentage change": "projected_change",
            "time horizon": "time_horizon",
            "confidence": "confidence"
        }

        def flush():
            if current_key and buffer:
                text = "\n".join(buffer).strip()
                output[current_key] = text
            buffer.clear()

        for line in lines:
            stripped = line.strip().lower().rstrip(":")
            if stripped in mapping:
                flush()
                current_key = mapping[stripped]
            elif current_key:
                buffer.append(line)

        flush()

        # Postprocess types
        try:
            if output["projected_change"]:
                match = re.search(r"([-+]?\d*\.?\d+)", output["projected_change"])
                if match:
                    output["projected_change"] = float(match.group(1))
        except Exception:
            output["projected_change"] = None

        try:
            if output["time_horizon"]:
                match = re.search(r"(\d*\.?\d+)", output["time_horizon"])
                if match:
                    output["time_horizon"] = float(match.group(1))
        except Exception:
            output["time_horizon"] = None

        try:
            if output["confidence"]:
                match = re.search(r"(\d*\.?\d+)", output["confidence"])
                if match:
                    output["confidence"] = float(match.group(1))
        except Exception:
            output["confidence"] = None

        return output


if __name__ == "__main__":
    utils = Utils()
    example = """
    Justification:  
    NVDA's recent earnings beat estimates and AI GPU demand is surging. Short-term upside is highly probable. 

    Position:  
    Buy

    Asset:  
    NVIDIA

    Projected Percentage Change:  
    +5.4%

    Time Horizon:  
    24 hours

    Confidence:  
    0.87
    """

    parsed = utils.parse_agent_output(example)
    print(parsed)
    
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
    
    print(utils.get_similarity(example, second_example))
