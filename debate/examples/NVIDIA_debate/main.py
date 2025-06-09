"""
This is a simple example of how to use the debate module.
It will run a debate on the NVIDIA stock price and output the final position.
"""

from debate.debate import Debate
from debate.examples.NVIDIA_debate.data import data
from debate.examples.NVIDIA_debate.prompts import Prompts
from debate.examples.NVIDIA_debate.utils import Utils
from reasoning.llm import LLM

import time


def main():
    time_start = time.time()
    print("Starting NVIDIA Trading Debate...")
    
    print("Initializing components...")
    prompts = Prompts()
    util = Utils()
    llm = LLM()
    print("Components initialized successfully")
    
    print("Creating debate instance...")
    debate = Debate(debate_name="NVIDIA_TRADING_DEBATE", data=data, prompts=prompts, util=util, llm=llm)
    print("Debate instance created")
    
    print("Initializing debate...")
    debate.initialize()
    print("Debate initialized successfully")
    print("Running debate with 3 rounds and 1 hidden layer...")
    debate.run_debate(num_rounds=3, num_hidden_layers=1)
    print("Debate completed!")
    
    time_end = time.time()
    print(f"Final position: {debate.final_position}")
    
    print("Saving debate results...")
    with open("debate/examples/NVIDIA_debate/debate.txt", "w") as f:
        f.write(f'Time taken: {time_end - time_start} seconds\n\n' + debate.get_debate())
    print("Results saved to debate.txt")
    
    print(f"Total time taken: {time_end - time_start:.2f} seconds")
    
if __name__ == "__main__":
    main()
    
    
# Static vs Dynamic
# Rounds Layers
# When we add in static
# Full debate vs one shot prompt, one cluster
# How much data to give to different agents
# Compare against existing debates
# TODO fix categorization & integrate portfolio manager