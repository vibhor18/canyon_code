import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools_mcp.tools import (
    ToolContext, get_table_schema, list_feeds, filter_and_rank_feeds,
    get_encoder_params, get_decoder_params, summarize_selection
)
from tools_mcp.schemas import (
    GetTableSchemaRequest, ListFeedsRequest, FilterAndRankRequest,
    GetEncoderParamsRequest, GetDecoderParamsRequest, SummarizeSelectionRequest
)

def main():
    ctx = ToolContext(data_dir=".")
    print("Schema sample:", get_table_schema(ctx, GetTableSchemaRequest()).columns[:2])

    lf = list_feeds(ctx, ListFeedsRequest(limit=5))
    print("List feeds sample count:", len(lf.feeds))

    fr = filter_and_rank_feeds(ctx, FilterAndRankRequest(top_k=5))
    print("Top ranked FEED_IDs:", [r.FEED_ID for r in fr.feeds])

    enc = get_encoder_params(ctx, GetEncoderParamsRequest())
    dec = get_decoder_params(ctx, GetDecoderParamsRequest())
    print("Encoder keys:", list(enc.params.keys())[:5])
    print("Decoder keys:", list(dec.params.keys())[:5])

    if fr.feeds:
        ids = [fr.feeds[0].FEED_ID]
        sm = summarize_selection(ctx, SummarizeSelectionRequest(feed_ids=ids))
        print("Summary first row:", sm.rows[0].model_dump())

if __name__ == "__main__":
    main()
