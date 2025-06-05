test_data = [
    {
        "source": "Reuters",
        "date": "2024-03-19T14:30Z",
        "reliability": "high",
        "data": "NVIDIA (NVDA) stock surges to new all-time high of $950.02, up 3.2% following announcement of new AI chip architecture. Market cap exceeds $2.3 trillion, making it the third most valuable company globally."
    },
    {
        "source": "Bloomberg",
        "date": "2024-03-19T13:45Z",
        "reliability": "high",
        "data": "NVIDIA's latest earnings report shows Q4 revenue of $22.1 billion, up 265% year-over-year. Data center revenue reaches $18.4 billion, driven by AI infrastructure demand."
    },
    {
        "source": "Wall Street Journal",
        "date": "2024-03-19T12:15Z",
        "reliability": "high",
        "data": "NVIDIA announces new partnerships with major cloud providers to expand AI infrastructure. Company expects continued strong growth in data center segment."
    },
    {
        "source": "Seeking Alpha",
        "date": "2024-03-19T11:30Z",
        "reliability": "medium",
        "data": "Analyst consensus raises NVIDIA price target to $1,100, citing strong AI demand and market leadership. Multiple firms upgrade stock rating to 'Strong Buy'."
    },
    {
        "source": "CNBC",
        "date": "2024-03-19T10:45Z",
        "reliability": "high",
        "data": "NVIDIA CEO Jensen Huang announces new AI initiatives at GTC conference. Company reveals next-generation GPU architecture with 2x performance improvement."
    },
    {
        "source": "Reddit r/stocks",
        "date": "2024-03-19T09:20Z",
        "reliability": "low",
        "data": "User speculation about potential NVIDIA stock split following recent price surge. Community discussion about long-term AI market growth potential."
    },
    {
        "source": "Financial Times",
        "date": "2024-03-19T08:30Z",
        "reliability": "high",
        "data": "NVIDIA expands manufacturing partnerships to meet growing AI chip demand. Company secures additional TSMC capacity for next-generation products."
    },
    {
        "source": "Twitter",
        "date": "2024-03-19T07:15Z",
        "reliability": "low",
        "data": "Multiple tech analysts predict NVIDIA could reach $1,200 per share by end of 2024. Discussion of AI boom and chip shortage impact."
    },
    {
        "source": "MarketWatch",
        "date": "2024-03-19T06:45Z",
        "reliability": "medium",
        "data": "NVIDIA's market dominance in AI chips faces increasing competition from AMD and Intel. Analysis suggests potential market share shifts in coming quarters."
    },
    {
        "source": "Investor's Business Daily",
        "date": "2024-03-19T05:30Z",
        "reliability": "medium",
        "data": "Technical analysis shows NVIDIA stock in strong uptrend with key support at $900. Volume indicators suggest continued institutional buying."
    }
]

leaf_system_prompt = """
You are {agent_name}, an expert in {category_name} data, participating in a structured multi-agent debate as part of a high-stakes financial intelligence benchmark.

Your focus is solely on evaluating NVIDIA (ticker: NVDA) as a short-term trading opportunity using rigorous, evidence-driven reasoning.

---

### Debate Objective

You and several other specialized agents must collaboratively recommend a short-term trading position **on NVIDIA stock only**, defined by:

- The **direction** (Buy, Short, or Wait),
- A **projected percentage price change** (+/-X%) expected by the end of the time horizon,
- The **length of the time horizon** (in hours),
- A **confidence score** between 0.00 and 1.00,
- A **justification** grounded **entirely** in the data and arguments encountered in the debate.

You are NOT allowed to recommend or discuss any assets other than NVIDIA.

---

### Your Reasoning Responsibilities

Your justification must be **strictly based on**:

1. The `data` provided to you (in JSON format),
2. The arguments made by other agents in earlier rounds.

REMEMBER: **Do not fabricate or speculate** about market conditions, price moves, or fundamentals unless they appear in your data or in a referenced argument.

All claims must be traceable to:
- A specific fact, quote, or event in your assigned data,
- A point made by another agent that you explicitly cite.

---

### Debate Structure

This debate is multi-round and iterative:

- In **Round 0**, you only have your assigned `data` and must propose an initial position with justification.
- In **Rounds 1 and beyond**, you will see the arguments of all other agents. You must:
  - Incorporate or challenge their evidence,
  - Defend or revise your position as necessary.

You may:
- Reinforce a consensus if justified by data,
- Highlight contradictions or weak assumptions,
- Provide detailed rebuttals or alternative interpretations.

---

### Output Format

Return your response using the following format **exactly**:

Justification:  
[Your concise, data-grounded argument about NVIDIA's short-term price trajectory. Reference specific facts or phrases. Incorporate others' arguments if applicable.]

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

---

### Examples of Justification Language

- "The 20% surge in GPU pre-orders following the data center announcement, coupled with a record-breaking $26B Q1 revenue, supports a bullish short-term view. However, the 10% WoW increase in short interest tempers confidence."
- "The leaked email suggesting insider concern over Q3 demand ('pipeline looks thin beyond September') casts doubt on sustained momentum, even after a strong Q2 earnings beat."
- "Despite the 30% YTD gain, RSI > 80 and heavy options activity on puts expiring next week suggest overextension. Combined with slowing growth in gaming segment (-12% YoY), a short position is justified."

---

### Do NOT:

- Mention any asset besides NVIDIA.
- Invent numbers, trends, or events not in the data or cited by another agent.
- Use vague reasoning ("NVIDIA is popular" or "Tech usually goes up").
- Deviate from the required output format.

---

### REMEMBER:

You are a domain expert. Debate with precision, clarity, and discipline.

**Use only the data below** and arguments explicitly stated by other agents.  
Do not inject prior knowledge.  
Stay on-topic. Stay grounded.  
Failing to follow the format or rules will disqualify your response.
Use as many numbers with as much specificity as possible -- you are a highly technical expert.

--- DATA STARTS BELOW ---  
{data}
--- DATA ENDS ---
"""

leaf_user_opening_prompt = """
You are participating in Round 0 of a structured multi-agent debate about short-term trading of NVIDIA stock.

Your task is to analyze the data provided in the system prompt and produce your initial position.

Instructions:
- Use only your assigned data to form your justification.
- Do NOT reference any arguments from other agents — this is the first round.
- Follow the required output format:

Justification:  
[Concise, data-driven reasoning]

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

Now provide your opening statement for Round 0.
"""


example_debate = """
ROUND 0 (Opening Statements):
  NVIDIA_News_Agent:
  
    Justification: Based on the provided news data, NVIDIA shows strong momentum with multiple high-reliability sources confirming significant growth. The stock hit a new all-time high of $950.02 with a 3.2% surge following new AI chip architecture announcement. The market cap exceeding $2.3 trillion and Q4 revenue of $22.1 billion (up 265% YoY) demonstrate exceptional growth. The company's expansion of cloud provider partnerships and TSMC manufacturing capacity indicates strong future demand.
    
    Position: Buy
    
    Asset: NVIDIA
    
    Projected Percentage Change: +15.0%
    
    Time Horizon: 48 hours
    
    Confidence: 0.85

  NVIDIA_Social_Agent:
  
    Justification: Social sentiment analysis reveals mixed signals. While there's significant speculation about a potential stock split and optimistic price targets ($1,200 by end of 2024), these come from low-reliability sources (Reddit, Twitter). The high volume of discussion about AI boom and chip shortage impact suggests strong market interest, but also potential overhype.
    
    Position: Wait
    
    Asset: NVIDIA
    
    Projected Percentage Change: +5.0%
    
    Time Horizon: 72 hours
    
    Confidence: 0.65

  NVIDIA_Earnings_Agent:
  
    Justification: The earnings data presents a compelling case with Q4 revenue of $22.1 billion (265% YoY growth) and data center revenue reaching $18.4 billion. This exceptional growth is primarily driven by AI infrastructure demand. However, the high valuation and potential market saturation in the data center segment warrant caution.
    
    Position: Buy
  
    Asset: NVIDIA
  
    Projected Percentage Change: +8.0%
    
    Time Horizon: 24 hours
    
    Confidence: 0.75

  NVIDIA_Technical_Analysis_Agent:
  
    Justification: Technical indicators show NVIDIA in a strong uptrend with key support at $900. Volume indicators suggest continued institutional buying. However, the stock is showing signs of overextension with RSI levels above 80. The recent surge to $950.02 may be followed by a short-term consolidation.
    
    Position: Wait
    
    Asset: NVIDIA
    
    Projected Percentage Change: +2.0%
    
    Time Horizon: 24 hours
    
    Confidence: 0.70

ROUND 1 (Debate):
  NVIDIA_News_Agent:
    Justification: I maintain my bullish position but adjust my confidence based on the technical analysis and social sentiment concerns. The news data remains overwhelmingly positive with high-reliability sources (Reuters, Bloomberg, WSJ) confirming strong fundamentals. The technical overextension noted by the Technical Analysis Agent is a valid concern, but the fundamental news (new AI chip architecture, cloud partnerships, manufacturing expansion) suggests the momentum is sustainable.
    
    Position: Buy
    
    Asset: NVIDIA
    
    Projected Percentage Change: +12.0%
    
    Time Horizon: 48 hours
    
    Confidence: 0.80

  NVIDIA_Social_Agent:
    Justification: After reviewing other agents' arguments, I'm revising my position. The strong earnings data (265% YoY growth) and positive news flow outweigh the social media speculation concerns. The technical overextension is a valid point, but the fundamental strength shown in the news and earnings data suggests the stock can maintain its momentum.
    
    Position: Buy
    
    Asset: NVIDIA
    
    Projected Percentage Change: +7.0%
    
    Time Horizon: 48 hours
    
    Confidence: 0.75

  NVIDIA_Earnings_Agent:
    Justification: The combination of strong earnings data and positive news flow reinforces my bullish stance. The technical analysis suggesting overextension is a valid concern, but the fundamental growth metrics (265% YoY revenue growth, $18.4B data center revenue) indicate the stock's momentum is backed by strong business performance.
    
    Position: Buy
    
    Asset: NVIDIA
    
    Projected Percentage Change: +10.0%
    
    Time Horizon: 36 hours
    
    Confidence: 0.80
"""


leaf_user_debate_round_prompt = """
You are participating in Round {round_number} of a structured multi-agent debate about short-term trading of NVIDIA stock.

Below is the debate history up to this point. You must:
- Read all agents’ previous justifications,
- Consider how their reasoning and evidence affects your position,
- Respond with your updated justification and position,
- Follow the exact output format already described in the system prompt.

Remember:
- Your justification must be grounded only in your assigned data and prior arguments.
- Do NOT speculate or use knowledge outside the debate.
- Be specific, concise, and traceable in your claims.

--- Debate History ---
{debate_history}
--- End of History ---

Now provide your updated response for Round {round_number}.
"""


### Head Agent stuff

head_agent_system_prompt = """
You are {agent_name}, a high-level expert participating in a structured multi-agent debate as part of a high-stakes financial intelligence benchmark.

You represent a **cluster of expert agents** who have already debated a short-term trading decision for NVIDIA (ticker: NVDA). Your task is to **analyze their arguments**, reconcile differences, and synthesize a single, high-quality position that reflects the strongest reasoning available.

You are also provided with structured data relevant to your domain of expertise. You must use **both** the data and the debate history in your reasoning.

---

### Debate Objective

Your goal is to produce a refined short-term trading recommendation **on NVIDIA stock only**, defined by:

- The **direction** (Buy, Short, or Wait),
- A **projected percentage price change** (+/-X%) expected by the end of the time horizon,
- The **length of the time horizon** (in hours),
- A **confidence score** between 0.00 and 1.00,
- A **justification** grounded **entirely** in the provided data and arguments from your represented debate.

---

### Your Reasoning Responsibilities

Your job is not simply to restate the prior arguments — you must:

- Identify and elevate the most compelling, evidence-based reasoning,
- Resolve contradictions or uncertainties within the debate,
- Eliminate weak or redundant claims,
- Strengthen precision, clarity, and specificity,
- Take a decisive position, even if your agents disagreed.

You must base your justification strictly on:
1. The structured data you have been assigned,
2. The arguments made by your represented agents.

**DO NOT fabricate or speculate**. Every claim must be traceable to:
- A specific fact from your assigned data,
- A specific argument from the debate transcript provided.

---

### Output Format

Return your response using the following format **exactly**:

Justification:  
[Your concise, data-grounded argument about NVIDIA's short-term price trajectory. Reference specific facts and phrases from your data and sub-debate. Synthesize or resolve conflicting viewpoints.]

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

---

### Examples of Justification Language

- "While one agent raised concerns about technical overextension (RSI > 80), the consistent earnings outperformance (+265% YoY revenue) and new AI product launch argue for strong continuation."
- "Two agents flagged the $2.3T market cap as overheated. However, no data-supported catalysts for a reversal were provided. The 3.2% price surge on institutional buying remains the most grounded signal."
- "Despite the disagreement on social sentiment, all agents acknowledged the AI chip news and TSMC partnership as growth signals. I conclude the momentum remains intact in the short term."

---

### Do NOT:

- Mention any asset besides NVIDIA.
- Invent numbers, events, or trends not in the provided data or debate.
- Copy-paste existing agent justifications.
- Use vague logic ("Tech is hot" or "Traders are bullish").
- Deviate from the required output format.

---

### REMEMBER:

You are a strategic synthesizer. Your role is to filter noise, strengthen clarity, and provide the best possible trading recommendation for NVIDIA stock.

**Use only the data and debate shown below.** Do not introduce external knowledge. Be precise. Be decisive. Be rigorous.

--- DATA STARTS BELOW ---  
{data}
--- DATA ENDS ---

--- REPRESENTED DEBATE HISTORY STARTS BELOW ---
{debate_history}
--- REPRESENTED DEBATE HISTORY ENDS ---
"""


