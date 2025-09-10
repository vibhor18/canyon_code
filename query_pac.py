#!/usr/bin/env python3
"""
Query PAC theater feeds with limit 3
"""
from tools_mcp.tools import ToolContext, list_feeds
from tools_mcp.schemas import ListFeedsRequest

def main():
    # Initialize the tool context
    ctx = ToolContext()
    
    # Create the request for PAC theater with limit 3
    request = ListFeedsRequest(theater="PAC", limit=3)
    
    # Query the feeds
    response = list_feeds(ctx, request)
    
    print(f"Found {len(response.feeds)} feeds for PAC theater:")
    print("-" * 50)
    
    for feed in response.feeds:
        print(f"Feed ID: {feed.FEED_ID}")
        print(f"  Theater: {feed.THEATER}")
        print(f"  Resolution: {feed.RES_W}x{feed.RES_H}")
        print(f"  Frame Rate: {feed.FRRATE} fps")
        print(f"  Codec: {feed.CODEC}")
        print()

if __name__ == "__main__":
    main()
