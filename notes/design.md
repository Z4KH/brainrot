# Design

Data -> Debate -> Categories
- Categories are split up by LLM which assigns multiple entries to a given category
- each data entry is given the "category" key and assigned the category
- Within a given category, entries are grouped into "Agents" based on token quantity (there is a token limit to each agent's data)
- These agents all form a "Cluster"

### Full Debate begins:
- Each cluster has an internal debate
- A head agent is then formed to represent the cluster (includes the debate & data in the initial prompt)
- head agent gives opening statement -> New clusters are formed based on maximizing the differences between agents within the same cluster - `compare` function returns a difference -> forms a dict of differences, clusters are formed to maximize the total differences within the cluster
- cycle repeats until debate ends (`num_layers`) 

### Cluster formation algorithm:
Compute num clusters C_i based on previous C_prev and num_rounds
For each head_agent:
    for each cluster:
        simulate cluster += head_agent
        compute change in diversity_score(cluster) (weighted by size of cluster relative to target size)
    add head_agent to cluster with greatest positive change in diversity_score

### Final Decision:
After get_final_decision is called on the final agent/s

## Cluster

### Attributes
- Debate
- Agents
- cluster_name (Category name for layer 1, cluster{i} for upper layers)
- head_agent

### Internal Debate
- Each agent in the cluster has already given their opening statement(based on data) upon arriving in the cluster
- They are given all other agent's prior statements and asked to make a new statement 
- runs for num_rounds
- then head agent is synthesized

### Memory
- Includes a memory of the debate:
```python
rounds = [
    {
        "Agent1": "..."
        "Agent2": "..."
    },
    {
        "Agent1": "..."
        "Agent2": "..."
    },
]
```
- Formats the debate memory as a string and passes it into each debate_agent for each prompt in each round
- passes the full debate memory into the head_agent synthesis

## Agents

### Debate Agent
- Base level class
- Contains a SYSTEM PROMPT, data, past_debate(for head agents), user_prompt
- generate opening statement
- generate argument
- represented_agents (for head agent)
- represented debate (for head agent)
- role (leaf agent/head agent)

### Naming Conventions
- Category Agents {DEBATE_NAME}_{CATEGORY}_Agent{i}
- Category Head Agents (1st Layer) {DEBATE_NAME}_{CATEGORY}_HeadAgent
- Cluster Head Agents (Past 1st Layer) {DEBATE_NAME}_Cluster{representing_cluster_idx}_Layer{layer_idx}_HeadAgent

## Stock Trading
### Response Format:
```python
"""
Justification:  
[Your concise, data-grounded argument about NVIDIA’s short-term price trajectory. Reference specific facts or phrases. Incorporate others’ arguments if applicable.]

Position:  
[Buy / Short / Wait]

Asset:  
NVIDIA

Projected Percentage Change:  
[+/-X.X%]

Time Horizon:  
[X hours]

Confidence:  
[0.00 to 1.00]
"""
```

### Data Format
```python
data = [
    {
            "source": "Reuters
            "date": "2025-05-09T12:10Z", 
            "reliability": "high",
            "data": "BREAKING: Elon Musk announces he's changing his name to 'ClownCoin' and launching a new cryptocurrency"
    }
]
```

### Util Class
- Provided by user so that framework can work well
```python
def format_agent_response(response):
    """
    User provides a function that takes the agent's response and formats it in a dict
    """

def draw_final_conclusion(response):
    """
    Based on the agent response determine final standpoint of agent
    """

def compare_responses(response1, response2):
    """
    A function that compares the responses of two agents and returns the difference as a number
    """
```

### Prompts class (provided by user)
```python
class Prompts:
    format_leaf_agent_system_prompt(agent_name, category, data)
```


## Static Agents
- Each have all the data, but differring personalities
- Every cluster must have at least one dynamic agent, but can have several static agents
- Cluster only debates if the following cases are met:
    - There are multiple agents
    - There are multiple dynamic agents or the diversity of the cluster is high
- Final head agent is either created or in the case when the cluster has not debated, just the first dynamic agent
- replaced string literal for debate_agent role with an enum