#!/usr/bin/env python3
"""
Query EUR theater feeds with top_k=5 (ranked by clarity)
"""
from tools_mcp.tools import ToolContext, filter_and_rank_feeds
from tools_mcp.schemas import FilterAndRankRequest

def main():
    # Initialize the tool context
    ctx = ToolContext()
    
    # Create the request for EUR theater with top_k=5
    request = FilterAndRankRequest(theater="EUR", top_k=5)
    
    # Query and rank the feeds
    response = filter_and_rank_feeds(ctx, request)
    
    print(f"Top {len(response.feeds)} ranked feeds for EUR theater:")
    print("-" * 60)
    
    for i, feed in enumerate(response.feeds, 1):
        print(f"{i}. Feed ID: {feed.FEED_ID}")
        print(f"   Theater: {feed.THEATER}")
        print(f"   Resolution: {feed.RES_W}x{feed.RES_H}")
        print(f"   Frame Rate: {feed.FRRATE} fps")
        print(f"   Codec: {feed.CODEC}")
        print(f"   Clarity Score: {feed.clarity_score:.3f}")
        print()

if __name__ == "__main__":
    main()
