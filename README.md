# BRAINROT: Behavioural Reasoning Agent for Inference & Natural-language Risk Optimization in Trading

## Setup:
- Set TOGETHER_API_KEY or GROQ_API_KEY as an environment variable
- install requirements.txt

## Breakdown:
- Zach - Advanced debate framework (hierarchical & gorup based debate)
- Ryan - Reinforcement Section
- Jacob - Static agent allocation & Action layer
- Jeff - Research section & Sever

## TODO:
- research section
    - list of sources links to look at in sources.txt -> ingestion
        - or pre-existing deep research library
    - do simple NLP to highlight significant sentences/phrases in source, and output data as specified in bottom of information_transfer.py -> filtering
- finish processing section
    - hierarchical & group based debate structure
    - list of assets to debate over extracted from data or specifically inputted
    - list of relevant points to consider inputted from user
    - enforce argumentation with data in justifications
    - add roles/personalities (risk-taker, etc.)
    - action layer -- actual interface with the market -> output trade and projections for reinforcement layer
- reinforcement section (maybe grade sources/grade agent types/fine tune)
    - consistently monitor all trades
    - determine when to sell
    - fine tune model or update some explicit weights for sources/agent types based on performance
- figure out how to run continuous loop
    - Set up cheap server
- run experiment


## Changes:
- updated todos (zach)
    - just edited todos in readme
    
- simple debate layer (zach)
    - implemented naive running of debate
    - debate takes a long time
    - agents don't justify with data (need to use data in every justification)
    - hierarchy model would definitely be better

- debate round 0 (zach)
    - transfer info in round 0 of debate
    - added several prompts
    - refactored Agent -> DebateAgent

- finished simple information transfer layer (zach)
    - wrote create_agents method

- added simple data segmentation (zach)
    - need to do agent transfer next
    - started information transfer layer with data segmentation

- init (zach)
    - implemented simple agent with memory
    - implemented llm class
    - Created repo

- Broker (Jacob)
    - implemented broker class that allows agents to buy/sell/access stocks via Robinhood
    - created .env file to store login information
    - added .env file to list of files on .gitignore