# BRAINROT: Behavioural Reasoning Agent for Inference & Natural-language Risk Optimization in Trading

## Setup:
- Set TOGETHER_API_KEY or GROQ_API_KEY as an environment variable 

## TODO:
- research section (maybe some deep research repo, or input list of sources)
- reinforcement section (maybe grade sources/grade agent types/fine tune)
- action layer
- hierarcical debate structure
- require that the agents argue with data in justifications in debate prompt
- possibly input list of important points to consider for agents


## Changes:
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