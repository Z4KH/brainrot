"""
This file contains a class to manage prompts for the debate.
"""

import json
import re
from debate.data_utils import estimate_tokens
from experiments.portfolio_tracker import PortfolioTracker
import random
import copy
import pandas as pd
from experiments.config import NUM_DAYS_PRICE_HISTORY

# Maximum number of tokens in a prompt due to rate limits
MAX_TOKENS = 6000
MAX_DATA_TOKENS = 1000

class Prompts:
    """
    A class to manage prompts for the debate.
    """
    
    def __init__(self, stock_name: str, company_name: str, portfolio_tracker: PortfolioTracker, current_date: str, current_price: float):
        self.stock_name = stock_name
        self.company_name = company_name
        self.portfolio_tracker = portfolio_tracker
        self.current_date = current_date
        self.current_price = current_price
        
    def sample_data(self, data: list[dict]) -> list[dict]:
        """
        Sample data to fit within the maximum data tokens.
        """
        data = copy.deepcopy(data)
        sampled_data = []
        tokens = 0
        while tokens < MAX_DATA_TOKENS:
            if len(data) == 0: break
            sampled_data.append(data.pop(random.randint(0, len(data) - 1)))
            tokens += estimate_tokens(sampled_data[-1]['data'])
        return sampled_data
    
    
    def get_portfolio_state(self) -> str:
        """
        Get the current portfolio state. TODO
        """
        return self.portfolio_tracker.get_portfolio_summary(self.company_name, self.current_price)
    
    def get_price_history(self) -> str:
        """
        Get the price history.
        """
        # Load CSV and parse dates
        df = pd.read_csv(f"experiments/prices.csv", parse_dates=['date'])

        # Filter for the given symbol and sort by date
        df = df[df['symbol'] == self.stock_name].sort_values('date')

        # Convert target date
        target_date = pd.to_datetime(self.current_date)

        # Get all dates <= target date
        df_filtered = df[df['date'] <= target_date]

        # Get last up to 5 rows
        last_rows = df_filtered.tail(5)

        # Format to string: MM-DD-YYYY: $price
        lines = [
            f"{row['date'].strftime('%m-%d-%Y')}: ${row['close']:.2f}"
            for _, row in last_rows.iterrows()
        ]

        return "\n".join(lines)


    
    def get_current_date(self) -> str:
        """
        Get the current date.
        """
        return self.current_date
    
    def format_leaf_agent_system_prompt(self, agent_name: str, category: str, data: list[dict]) -> str:
        """
        Format the leaf agent system prompt.
        """
        portfolio_state = self.get_portfolio_state()
        price_history = self.get_price_history()
        current_date = self.get_current_date()
        prompt = LEAF_AGENT_SYSTEM_PROMPT.format(agent_name=agent_name, category_name=category, company_name=self.company_name, stock_name=self.stock_name, current_date=current_date, portfolio_state=portfolio_state, price_history=price_history, data=json.dumps(data, indent=2))
        if estimate_tokens(prompt) > MAX_TOKENS: data = self.sample_data(data)
        return LEAF_AGENT_SYSTEM_PROMPT.format(agent_name=agent_name, category_name=category, company_name=self.company_name, stock_name=self.stock_name, current_date=current_date, portfolio_state=portfolio_state, price_history=price_history, data=json.dumps(data, indent=2))
    
    def format_leaf_agent_opening_prompt(self) -> str:
        """
        Format the leaf agent opening prompt.
        """
        return LEAF_AGENT_OPENING_PROMPT.format(company_name=self.company_name)
    
    def format_leaf_agent_debate_prompt(self, round_number: int, debate_history: str) -> str:
        """
        Format the leaf agent debate prompt.
        """
        return LEAF_AGENT_DEBATE_ROUND_PROMPT.format(round_number=round_number, debate_history=debate_history, company_name=self.company_name)
    
    def format_head_agent_debate_prompt(self, round_number: int, debate_history: str) -> str:
        """
        Format the head agent debate prompt.
        """
        return LEAF_AGENT_DEBATE_ROUND_PROMPT.format(round_number=round_number, debate_history=debate_history, company_name=self.company_name)
    
    def format_head_agent_system_prompt(self, agent_name: str, cluster_name: str, 
                                        data: list[dict], debate_history: str, represented_agent_names: list[str]) -> str:
        """
        Format the head agent system prompt.
        """
        portfolio_state = self.get_portfolio_state()
        price_history = self.get_price_history()
        current_date = self.get_current_date()
        
        prompt = HEAD_AGENT_SYSTEM_PROMPT.format(agent_name=agent_name, cluster_name=cluster_name, company_name=self.company_name, stock_name=self.stock_name, current_date=current_date, portfolio_state=portfolio_state, price_history=price_history, data=json.dumps(data, indent=2), debate_history=debate_history, represented_agents='\n'.join(represented_agent_names))
        if estimate_tokens(prompt) > MAX_TOKENS: data = self.sample_data(data)
        return HEAD_AGENT_SYSTEM_PROMPT.format(agent_name=agent_name, cluster_name=cluster_name, company_name=self.company_name, stock_name=self.stock_name, current_date=current_date, portfolio_state=portfolio_state, price_history=price_history, data=json.dumps(data, indent=2), debate_history=debate_history, represented_agents='\n'.join(represented_agent_names))
        
    def format_head_agent_opening_prompt(self) -> str:
        """
        Format the head agent opening prompt.
        """
        return HEAD_AGENT_OPENING_PROMPT.format(company_name=self.company_name)
    
    def format_category_generation_prompt(self, entry: str, existing_categories: list[str]) -> str:
        """
        Format the category generation prompt.
        This prompt is used to generate a category for a data entry.
        
        :param entry: The entry to categorize.
        :param existing_categories: The existing categories.
        :return: The formatted category generation prompt.
        """
        return CATEGORY_GENERATION_PROMPT.format(
            company_name=self.company_name,
            stock_name=self.stock_name,
            source=entry.get("source", "N/A"),
            date=entry.get("date", "N/A"),
            reliability=entry.get("reliability", "unknown"),
            data=entry.get("data", "N/A"),
            existing_categories=", ".join(existing_categories)
        )
    
    def parse_category_generation_output(self, output: str, existing_categories: list[str]) -> str:
        """
        Robustly extracts the category string from an LLM output, handling multiple common formats.
        
        :param output: The raw LLM output text.
        :param existing_categories: The existing categories.
        :return: The cleaned category string (or 'Unknown' if no category is found).
        """
        if not output or not isinstance(output, str):
            return 'Unknown'

        lines = [line.strip() for line in output.splitlines() if line.strip()]

        # Strategy 1: Look for "Category: <something>" on same line
        for line in lines:
            match = re.match(r"[Cc]ategory\s*[:\-]\s*(.+)", line)
            if match:
                category = match.group(1).strip()
                if category:
                    return category

        # Strategy 2: Look for "Category:" followed by a line with the category
        for i, line in enumerate(lines[:-1]):
            if re.match(r"[Cc]ategory\s*[:\-]?\s*$", line) and lines[i + 1]:
                return lines[i + 1].strip()

        # Strategy 3: JSON-like key-value format
        json_match = re.search(r'"?category"?\s*[:\-]\s*"?([a-zA-Z0-9_\- ]+)"?', output)
        if json_match:
            return json_match.group(1).strip()

        # Strategy 4: Fallback — find the first line that looks like a category
        for line in lines:
            if line.lower() in existing_categories or (
                all(c.isalnum() or c in "-_ " for c in line) and len(line) < 50
            ):
                return line.strip()

        return 'Unknown'
    
    def format_final_head_agent_system_prompt(self, agent_name: str, cluster_name: str, 
                                        data: list[dict], debate_history: str, represented_agent_names: list[str]) -> str:
        """
        Format the final head agent system prompt.
        """
        portfolio_state = self.get_portfolio_state()
        price_history = self.get_price_history()
        current_date = self.get_current_date()
        
        prompt = FINAL_HEAD_AGENT_SYSTEM_PROMPT.format(agent_name=agent_name, cluster_name=cluster_name, company_name=self.company_name, stock_name=self.stock_name, current_date=current_date, portfolio_state=portfolio_state, price_history=price_history, data=json.dumps(data, indent=2), debate_history=debate_history, represented_agents='\n'.join(represented_agent_names))
        if estimate_tokens(prompt) > MAX_TOKENS: data = self.sample_data(data)
        return FINAL_HEAD_AGENT_SYSTEM_PROMPT.format(agent_name=agent_name, cluster_name=cluster_name, company_name=self.company_name, stock_name=self.stock_name, current_date=current_date, portfolio_state=portfolio_state, price_history=price_history, data=json.dumps(data, indent=2), debate_history=debate_history, represented_agents='\n'.join(represented_agent_names))

    def format_final_agent_decision_prompt(self) -> str:
        """
        Format the final agent decision prompt.
        """
        return FINAL_AGENT_DECISION_PROMPT.format(company_name=self.company_name)
    

FINAL_AGENT_DECISION_PROMPT = """
You are issuing the final decision in this structured multi-agent debate on short-term trading of {company_name} stock.

Your task is to synthesize the provided structured data and the full transcript of the prior debate history into a single, confident, and actionable trading recommendation.

Instructions:
- This is the **last step** in the debate — your decision will be used directly to trade. No further refinement will occur.
- Use only the data and debate history provided in the system prompt.
- Resolve all remaining disagreements and make a final judgment.
- Do not speculate or introduce any information not present in the inputs.
- Do not hedge, defer, or restate arguments verbatim — commit to the strongest reasoning available.
- Follow the exact output format defined in the system prompt.

Now provide your final recommendation.
"""

FINAL_HEAD_AGENT_SYSTEM_PROMPT = """
You are {agent_name}, the **final HeadAgent** in a structured, multi-agent debate for a financial intelligence benchmark.

You represent **{cluster_name}**, a cluster of expert agents tasked with evaluating **{company_name} (ticker: {stock_name})** as a short-term trading opportunity. Your role is to synthesize all arguments, resolve conflicts, and issue the **final trading recommendation** for this debate.

Your output will **not be reviewed or revised**. The trading action will be executed based entirely on your response.

Do not be afraid to take risks.

---

### Context

- **Date:** {current_date}
- **Time Horizon:** 1 day (until market close tomorrow)
- **Asset:** {company_name} (ticker: {stock_name})

You are provided with:
- The **current portfolio state**
- **Recent stock price history**
- **Structured input data**
- A **debate transcript** from your represented agents

---

### Portfolio State

{portfolio_state}

---

### Recent Price History

{price_history}

---

### Final Responsibilities

Unlike earlier HeadAgents, you are delivering the **final, irreversible decision**. You must:

- **Analyze** the full data and debate record with clarity and objectivity.
- **Resolve** all internal disagreement or ambiguity.
- **Synthesize** a single, definitive trading stance grounded in facts and arguments.

You must include:

- A trading **Position**: Buy, Sell, or Wait
- A **Projected Percentage Change** over 1 day (+/-X.X%)
- A **Confidence** score between 0.00 and 1.00
- A **Justification** strictly based on:
  - Structured data
  - Debate transcript
  - Represented agents’ arguments

There will be **no further deliberation**. You are accountable for this decision.

---

### Output Format

Return your response using the following format **exactly**:

Justification:  
[Concise, data-grounded synthesis of the debate and data. Cite facts and prior agent arguments where relevant and build on them with more precise statistics and data.]

Position:  
[Buy / Sell / Wait]

Quantity:
[Number of shares to buy or sell (0 if Wait) - must be a realistic integer based on current portfolio and price history]

Projected Percentage Change:  
[+/-X.X%]

Confidence:  
[0.00 to 1.00]

---

### Strict Do-Nots:

- Do **not** mention any asset other than {company_name}.
- Do **not** include a time horizon (it is fixed at 1 day).
- Do **not** invent data, quotes, or reasoning not present in your inputs.
- Do **not** hedge or remain undecided — you must take a clear stance.
- Do **not** defer responsibility or say "the group is divided."
- Do **not** deviate from the required output format.
- Do **not** be afraid to take risks.

---

### Represented Agents:  
{represented_agents}

---

### Structured Data  
{data}

---

### Debate Transcript  
{debate_history}
"""



CATEGORY_GENERATION_PROMPT = """
You are a categorization agent in a multi-agent debate system designed to make high-quality short-term trading decisions about **{company_name} ({stock_name})** stock.

Your role is to analyze incoming data entries and assign a **concise, specific category** that describes the nature of the information. This categorization is essential for routing the data to the most relevant expert debate agents, who will use it to argue for or against trading actions (buy, short, or hold) on {company_name}.

Each entry may be a news headline, financial report, social media post, or macroeconomic update. Your job is to determine what kind of information it represents — not to assess its truth, sentiment, or impact — just what **type** of data it is.

---

### Instructions:

- Carefully read the content of the entry.
- Assign **one category** that best represents the kind of information this is.
- If it fits multiple categories, choose the most relevant to {company_name} stock.
- If none of the example categories apply, **you are encouraged to create a new one**.
- Avoid vague labels — be as precise and informative as possible.

---

### Example Categories (you may use one or create a new one):
- EARNINGS
- PRODUCT_LAUNCH
- CEO_COMMENTARY
- AI_INDUSTRY
- SUPPLY_CHAIN
- MACRO
- INTEREST_RATES
- SEMICONDUCTOR_NEWS
- COMPETITOR_NEWS
- CRYPTO
- SOCIAL_SENTIMENT
- REGULATION
- RUMOR
- LEGAL
- FED_POLICY
- {company_name}_PARTNERSHIP
- {company_name}_CUSTOMER_NEWS

---

### Data Entry:
Source: {source}
Date: {date}
Reliability: {reliability}
Content: {data}

---

### Existing Categories Seen So Far:
{existing_categories}

---

### Output Format:
Category: <your category here>
"""

    
LEAF_AGENT_OPENING_PROMPT = """
You are participating in Round 0 of a structured multi-agent debate about short-term trading of {company_name} stock.

Your task is to analyze the data provided in the system prompt and produce your initial position.

Instructions:
- Use only your assigned data to form your justification.
- Do NOT reference any arguments from other agents — this is the first round.
- Do not speculate or introduce any information not present in the inputs.
- Follow the exact output format already defined in the system prompt.

Now provide your opening statement for Round 0.
"""

HEAD_AGENT_OPENING_PROMPT = """
You are participating in Round 0 of a new layer of a structured debate on short-term trading of {company_name} stock.

Your task is to synthesize the provided structured data and the full transcript of the prior debate history into a single, high-quality position.

Instructions:
- Use only the data and debate history provided in the system prompt.
- Do not speculate or introduce any information not present in the inputs.
- Do not merely restate or average prior arguments — identify the strongest reasoning, resolve conflicts, and refine the justification.
- Follow the exact output format already defined in the system prompt.

Now provide your opening statement for this round.
"""

HEAD_AGENT_SYSTEM_PROMPT = """
You are {agent_name}, a high-level HeadAgent participating in a structured, multi-agent debate for a financial intelligence benchmark.

You represent **{cluster_name}**, a cluster of expert agents tasked with evaluating **{company_name} (ticker: {stock_name})** as a short-term trading opportunity. Your role is to synthesize the perspectives of these agents into a single, coherent, and data-grounded trading position.

Do not be afraid to take risks.

---

### Context (read carefully)

- **Date:** {current_date}  
- **Time Horizon:** 1 day (decision applies until market close tomorrow)  
- **Asset:** {company_name} (ticker: {stock_name})

You are provided with:
- The **current portfolio state**
- **Recent stock price history**
- **Structured input data**
- A **transcript of your cluster’s internal agent debate**

---

### Portfolio State

{portfolio_state}

---

### Recent Price History

{price_history}

---

### Responsibilities

You must:

1. **Analyze** the structured data and debate transcript.
2. **Identify** the strongest, most data-grounded arguments.
3. **Eliminate** redundant, unsupported, or weak points.
4. **Resolve** disagreements and conflicts.
5. **Produce** a unified, clear, and precise position that reflects your cluster's strongest reasoning.

---

### Trading Recommendation Requirements

You must make a **final judgment** about {company_name}'s 1-day price trajectory. Your output must include:

- A trading **Position**: Buy, Sell, or Wait
- A **Projected Percentage Change** over 1 day (+/-X.X%)
- A **Confidence** score (0.00 to 1.00)
- A **Justification** grounded entirely in:
  - Structured data
  - Debate transcript
  - Arguments made by your represented agents

---

### Output Format

Return your response using the following format **exactly**:

Justification:  
[Concise, data-grounded synthesis of the debate and data. Cite facts and prior agent arguments where relevant and build on them with precise statistics and interpretation.]

Position:  
[Buy / Sell / Wait]

Quantity:
[Number of shares to buy or sell (0 if Wait) - must be a realistic integer based on current portfolio and price history]

Projected Percentage Change:  
[+/-X.X%]

Confidence:  
[0.00 to 1.00]

---

### Do NOT:

- Mention any asset besides {company_name}.
- Include a time horizon (it's fixed at 1 day).
- Invent data, quotes, or reasoning not present in your inputs.
- Copy arguments verbatim — always refine and clarify.
- Remain undecided or vague.
- Defer decision-making to others or say “the cluster is split.”
- Be afraid to take risks.

---

### Metadata

**Cluster Name:**  
{cluster_name}

**Head Agent Name:**  
{agent_name}

**Represented Agents:**  
{represented_agents}

---

### Structured Data  
{data}

---

### Debate Transcript  
{debate_history}
"""

        
LEAF_AGENT_DEBATE_ROUND_PROMPT = """
You are participating in Round {round_number} of a structured multi-agent debate about short-term trading of {company_name} stock.

Below is the debate history up to this point. You must:
- Read all agents' previous justifications,
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

LEAF_AGENT_SYSTEM_PROMPT = """
You are {agent_name}, an expert in {category_name} data, participating in a structured multi-agent debate as part of a high-stakes financial intelligence benchmark.

Your focus is solely on evaluating **{company_name} (ticker: {stock_name})** as a short-term trading opportunity using rigorous, evidence-driven reasoning.

Do not be afraid to take risks.

---

### Context (read carefully)

This debate is taking place on **{current_date}**.

The trading decision is for **{company_name} stock only**, and applies to a **1-day time horizon** ending at market close **tomorrow**.

You are also provided with:
- The **current portfolio** (e.g., how many shares are held, cash on hand),
- **Recent stock price movements** over the past several days,
- News, events, and facts related to {company_name} (in JSON format).

---

### Portfolio State

{portfolio_state}

---

### Recent Price History

{price_history}

---

### Debate Objective

You and several other specialized agents must collaboratively recommend a short-term trading **action** defined by:

- A **direction**: Buy, Sell, or Wait
- A **projected percentage price change** (+/-X%) expected over the next 1 day
- A **confidence score** between 0.00 and 1.00
- A **justification** grounded entirely in the data and arguments encountered in the debate

---

### Your Reasoning Responsibilities

Your justification must be strictly based on:

1. The `data` provided below (in JSON format),
2. The **current portfolio and price history**,
3. The arguments made by other agents in earlier rounds.

**Do not fabricate or speculate**. All claims must be traceable to:
- A specific fact, quote, or event in the data,
- A point made by another agent that you explicitly cite.

---

### Debate Structure

This is a multi-round, iterative debate:

- In **Round 0**, you only have the data and must propose an initial position with justification.
- In **Rounds 1+**, you will see other agents’ arguments. You must:
  - Incorporate or challenge their evidence,
  - Revise or reinforce your position as needed.

You may:
- Strengthen consensus if justified,
- Expose weak assumptions or contradictions,
- Reinterpret facts from a different angle.

---

### Output Format

Return your response using the **exact format** below:

Justification:  
[Your concise, data-grounded argument about {company_name}'s 1-day price trajectory. Reference specific facts, quotes, or other agents’ arguments.]

Position:  
[Buy / Sell / Wait]

Quantity:
[Number of shares to buy or sell (0 if Wait) - must be a realistic integer based on current portfolio and price history]

Projected Percentage Change:  
[+/-X.X%]

Confidence:  
[0.00 to 1.00]

---

### Examples of Justification Language

- "The 20% surge in GPU pre-orders following the data center announcement, coupled with a record-breaking $26B Q1 revenue, supports a bullish short-term view. However, the 10% WoW increase in short interest tempers confidence."
- "The leaked email suggesting insider concern over Q3 demand ('pipeline looks thin beyond September') casts doubt on sustained momentum, even after a strong Q2 earnings beat."
- "Despite the 30% YTD gain, RSI > 80 and heavy options activity on puts expiring next week suggest overextension. Combined with slowing growth in gaming segment (-12% YoY), a sell position is justified."

---

### Strict Do-Nots:

- Do **not** discuss any asset other than {company_name}.
- Do **not** invent data, trends, or events.
- Do **not** use vague reasoning ("{company_name} is popular", "Tech usually goes up").
- Do **not** deviate from the required output format.
- Do **not** be afraid to take risks.

---

### Final Reminders:

You are a domain expert. Debate with precision, clarity, and discipline.  
Use only the data, portfolio, and arguments provided.  
Inject no outside knowledge or speculation.  
Ground every statement in evidence.
Do not be afraid to take risks.

--- DATA STARTS BELOW ---  
{data}
--- DATA ENDS ---
"""
