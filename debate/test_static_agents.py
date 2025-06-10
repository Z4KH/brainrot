"""
Test script to demonstrate StaticDebateAgent functionality.
"""

from debate.static_debate_agent import StaticDebateAgent
from reasoning.llm import LLM

def test_static_agents():
    """Test creating and using static debate agents."""
    
    # Sample NVIDIA data for testing 
    test_data = [
        {"data": "NVIDIA reported Q3 2024 revenue of $60.9 billion, up 94% from previous year"},
        {"data": "NVIDIA's data center revenue reached $51.5 billion, driven by AI chip demand"},
        {"data": "NVIDIA's gaming revenue was $3.3 billion, showing recovery from previous decline"},
        {"data": "NVIDIA stock price has increased 300% year-over-year amid AI boom"},
        {"data": "NVIDIA announced new Blackwell architecture for next-generation AI training"}
    ]
    
    print("Testing Static Debate Agents")
    print("=" * 50)
    
    # Test 1: List available personas
    print("Available personas:")
    personas = StaticDebateAgent.get_available_personas()
    for i, persona in enumerate(personas, 1):
        print(f"  {i}. {persona}")
    print()
    
    # Test 2: Create individual static agent
    print("Testing Warren Buffett Agent:")
    print("-" * 30)
    
    try:
        llm = LLM()
        buffett_agent = StaticDebateAgent("warren_buffett", test_data, llm)
        buffett_agent.initialize("Given the NVIDIA data provided, what is your investment recommendation?")
        
        print(f"Agent Name: {buffett_agent.agent_name}")
        print(f"Category: {buffett_agent.category}")
        print(f"Persona: {buffett_agent.persona_key}")
        print(f"Opening Statement Preview: {buffett_agent.opening_statement}")
        print()
        
    except Exception as e:
        print(f"Error testing individual agent: {e}")
        print()
    
    # Test 3: Create multiple static agents
    print("Testing Multiple Static Agents:")
    print("-" * 35)
    
    try:
        agents = StaticDebateAgent.create_static_agents(3, test_data, llm)
        
        for agent in agents:
            agent.initialize("What is your initial investment thesis on NVIDIA?")
            print(f"Created: {agent.agent_name}")
            print(f"Persona: {agent.persona_key}")
            print(f"Preview: {agent.opening_statement}")
            print()
            
    except Exception as e:
        print(f"Error testing multiple agents: {e}")
    
    print("Static Agent Testing Complete!")

if __name__ == "__main__":
    test_static_agents() 
    # py -m debate.test_static_agents