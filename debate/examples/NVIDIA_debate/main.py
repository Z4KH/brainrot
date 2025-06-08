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
    prompts = Prompts()
    util = Utils()
    llm = LLM()
    debate = Debate(debate_name="NVIDIA_TRADING_DEBATE", data=data, prompts=prompts, util=util, llm=llm)
    debate.initialize()
    debate.run_debate(num_rounds=3, num_hidden_layers=1)
    time_end = time.time()
    print(debate.final_position)
    with open("debate/examples/NVIDIA_debate/debate.txt", "w") as f:
        f.write(f'Time taken: {time_end - time_start} seconds\n\n' + debate.get_debate())
    print(f"Time taken: {time_end - time_start} seconds")
    
if __name__ == "__main__":
    main()