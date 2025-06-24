# 🧠 BRAINROT: Behavioral Reasoning Agent for Inference & Natural-language Risk Optimization in Trading

**Multi-Agent LLM System for Real-Time Financial Decision Making**

> 🚀 Unlock explainable, high-performance stock trading using Large Language Models and structured multi-agent debate.

![GitHub Repo Stars](https://img.shields.io/github/stars/Z4KH/brainrot?style=social)
![License](https://img.shields.io/github/license/Z4KH/brainrot)

---

## 📈 Overview

**BRAINROT** is a cutting-edge multi-agent financial reasoning framework that uses **Large Language Models (LLMs)** to make **short-term stock trading decisions** based on **real financial news**. Agents dynamically ingest, debate, and reason over real-world data to output explainable buy/sell/wait decisions.

Inspired by systems like **ai-hedge-fund** and **TradingAgents**, BRAINROT introduces:
- Modular **hierarchical debates**
- **Static personas** (e.g., Warren Buffett-style agents)
- **Dynamic clustering** for maximizing viewpoint diversity
- **Portfolio-aware trading actions**
- **Real-world evaluation with market slippage**

---

## 🔥 Key Features

- 🧩 **Agent roles**: Leaf, Static, Head, and Final Decision agents
- 🧠 **Diversity-maximizing clustering** and recursive debate hierarchy
- 📊 **Structured outputs**: Position, Quantity, Confidence, Projected Return
- 🧪 **Fully modular API** for custom prompts, utility functions, and new asset types
- 📉 **Realistic evaluation** using delayed execution to simulate slippage/gaps

---

## 🗂️ Examples

Quickstart example in the [`examples/`](./examples/) directory:

- `main.py`: Full multi-agent trading simulation for NVDA/TSLA/AAPL (depending on config.py & data imported)

---

## 🧠 Architecture

### Layered Reasoning System

```txt
      ┌──────────────────────────────┐
      │   Real-World Financial News  │
      └────────────┬─────────────────┘
                   ▼
           [ Categorization Layer ]
                   ▼
        ┌──────────────────────────┐
        │   Leaf & Static Agents   │ ← grounded, dynamic perspectives
        └────────────┬─────────────┘
                     ▼
         [ Cluster Round-Robin Debate ]
                     ▼
            Head Agents Synthesis
                     ▼
         [ Diversity-Based Reclustering ]
                     ▼
              Final Decision Agent
                     ▼
              🔻 Trade Execution 🔻

## TODO:
- get next cluster count at each iteration rather than at start - cluster counts may change
- Smarter way to add static agents than round robin(perhaps maximize diversity)
- Need to make StaticAgentRegistry (set of available static agents to select when running debate)
- Need to make additional StaticAgents class as input to debate for users to create their own static agents

