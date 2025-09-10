#!/usr/bin/env python3
"""
Explain what "best clarity" means in the context of this system
"""
from tools_mcp.tools import ToolContext, explain_term
from tools_mcp.schemas import ExplainTermRequest

def main():
    # Initialize the tool context
    ctx = ToolContext()
    
    # Create the request to explain "best clarity"
    request = ExplainTermRequest(phrase="best clarity")
    
    # Get the explanation
    response = explain_term(ctx, request)
    
    print("Explanation for 'best clarity':")
    print("=" * 40)
    print(f"Intent: {response.intent}")
    print(f"Weights: {response.weights}")
    print("Notes:")
    for note in response.notes:
        print(f"  - {note}")
    print()
    
    # Also show what feeds would be considered "best clarity"
    print("To find feeds with best clarity, the system would:")
    print(f"  - Prioritize resolution with weight: {response.weights['resolution']}")
    print(f"  - Consider frame rate with weight: {response.weights['fps']}")
    print(f"  - Factor in codec with weight: {response.weights['codec']}")

if __name__ == "__main__":
    main()
