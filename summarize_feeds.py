#!/usr/bin/env python3
"""
Summarize specific feeds by their IDs
"""
from tools_mcp.tools import ToolContext, summarize_selection
from tools_mcp.schemas import SummarizeSelectionRequest

def main():
    # Initialize the tool context
    ctx = ToolContext()
    
    # Create the request for the specific feed IDs
    request = SummarizeSelectionRequest(feed_ids=["FD-LLF3SB", "FD-8D150S"])
    
    # Get the summary
    response = summarize_selection(ctx, request)
    
    print(f"Summary for {len(response.rows)} selected feeds:")
    print("=" * 60)
    
    for i, feed in enumerate(response.rows, 1):
        print(f"{i}. Feed ID: {feed.FEED_ID}")
        print(f"   Theater: {feed.THEATER}")
        print(f"   Resolution: {feed.RES_W}x{feed.RES_H}")
        print(f"   Frame Rate: {feed.FRRATE} fps")
        print(f"   Codec: {feed.CODEC}")
        if feed.clarity_score is not None:
            print(f"   Clarity Score: {feed.clarity_score:.3f}")
        print()

if __name__ == "__main__":
    main()
