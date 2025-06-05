"""
This file is the main file for the project.
It is used to run the project.
"""

from processing.information_transfer import InformationTransfer
from processing.debate import Debate
from processing.debate_agent import DebateAgent


def main():
    # Load data
    test_data = [
        {
            "source": "Reuters | 2025-05-09T12:10Z | reliability: high",
            "data": "BREAKING: Elon Musk announces he's changing his name to 'ClownCoin' and launching a new cryptocurrency"
        },
        {
            "source": "Twitter | 2025-05-09T12:15Z | reliability: high",
            "data": "This is Elon Musk. I have NOT changed my name and I have NOT launched any cryptocurrency. Beware of scams."
        },
        {
            "source": "Reddit | 2025-05-09T13:40Z | reliability: medium",
            "data": "Just bought 1000 ClownCoin at $0.001, this is going to the moon!"
        },
        {
            "source": "Bloomberg | 2025-05-09T11:30Z | reliability: high",
            "data": "ClownCoin surges 500% after viral tweet from @elonmusk, but account appears to be fake"
        },
        {
            "source": "Twitter | 2025-05-09T14:20Z | reliability: low",
            "data": "ClownCoin is a scam! I lost all my life savings!"
        },
        {
            "source": "Reddit | 2025-05-09T15:00Z | reliability: medium",
            "data": "Technical analysis shows ClownCoin forming a bullish pennant pattern, breakout expected soon"
        },
        {
            "source": "CNBC | 2025-05-09T16:00Z | reliability: high",
            "data": "SEC launches investigation into ClownCoin after reports of market manipulation"
        },
        {
            "source": "Twitter | 2025-05-09T16:30Z | reliability: low",
            "data": "Just met @elonmusk at Tesla factory, he confirmed ClownCoin is legit!"
        },
        {
            "source": "WSJ | 2025-05-09T17:00Z | reliability: high",
            "data": "ClownCoin trading volume exceeds $1B in 24 hours, but 80% of transactions appear to be wash trading"
        },
        {
            "source": "Reddit | 2025-05-09T17:30Z | reliability: medium",
            "data": "My uncle works at Tesla and he says ClownCoin is actually a secret project by Elon"
        },
        {
            "source": "Twitter | 2025-05-09T18:00Z | reliability: high",
            "data": "This is Elon Musk. I am suing the creators of ClownCoin for using my name without permission."
        },
        {
            "source": "Reddit | 2025-05-09T18:30Z | reliability: low",
            "data": "ClownCoin devs just doxxed themselves, they're actually from North Korea!"
        }
    ]

    debate = Debate(test_data, '', 'What is the best way to invest in ClownCoin?')
    
        
    # Print debate
    for agent in agents:
        agent.output_conversation('out.txt')
    
    

if __name__ == "__main__":
    main()
