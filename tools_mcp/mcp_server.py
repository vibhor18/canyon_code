# tools_mcp/mcp_server.py
from __future__ import annotations
import json
from typing import Optional, List, Dict

from mcp.server.fastmcp import FastMCP

from tools_mcp.tools import (
    ToolContext,
    get_table_schema,
    list_feeds,
    filter_and_rank_feeds,
    get_encoder_params,
    get_decoder_params,
    summarize_selection,
    explain_term,
    sanity_check_constraints,
)

from tools_mcp.schemas import (
    GetTableSchemaRequest,
    ListFeedsRequest,
    FilterAndRankRequest,
    GetEncoderParamsRequest,
    GetDecoderParamsRequest,
    SummarizeSelectionRequest,
    ExplainTermRequest,
    SanityCheckRequest,
)

mcp = FastMCP("canyoncode-tools")
ctx = ToolContext(data_dir=".")


def _dump(model) -> dict:
    # Most tool returns are pydantic models
    return json.loads(model.model_dump_json()) if hasattr(model, "model_dump_json") else model


@mcp.tool()
def get_table_schema_tool() -> dict:
    """Return the camera table schema."""
    return _dump(get_table_schema(ctx, GetTableSchemaRequest()))


@mcp.tool()
def list_feeds_tool(
    theater: Optional[str] = None,
    min_res_w: Optional[int] = None,
    min_res_h: Optional[int] = None,
    min_fps: Optional[float] = None,
    codec_in: Optional[List[str]] = None,
    limit: int = 10,
) -> dict:
    """List feeds with optional filters."""
    req = ListFeedsRequest(
        theater=theater,
        min_res_w=min_res_w,
        min_res_h=min_res_h,
        min_fps=min_fps,
        codec_in=codec_in,
        limit=limit,
    )
    return _dump(list_feeds(ctx, req))


@mcp.tool()
def filter_and_rank_tool(
    theater: Optional[str] = None,
    min_res_w: Optional[int] = None,
    min_res_h: Optional[int] = None,
    min_fps: Optional[float] = None,
    codec_in: Optional[List[str]] = None,
    top_k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> dict:
    """Rank feeds by clarity with optional weights and filters."""
    req = FilterAndRankRequest(
        theater=theater,
        min_res_w=min_res_w,
        min_res_h=min_res_h,
        min_fps=min_fps,
        codec_in=codec_in,
        top_k=top_k,
        weights=weights,
    )
    return _dump(filter_and_rank_feeds(ctx, req))


@mcp.tool()
def get_encoder_params_tool() -> dict:
    """Return encoder parameters."""
    return _dump(get_encoder_params(ctx, GetEncoderParamsRequest()))


@mcp.tool()
def get_decoder_params_tool() -> dict:
    """Return decoder parameters."""
    return _dump(get_decoder_params(ctx, GetDecoderParamsRequest()))


@mcp.tool()
def summarize_selection_tool(feed_ids: List[str]) -> dict:
    """Summarize a list of feed IDs."""
    return _dump(summarize_selection(ctx, SummarizeSelectionRequest(feed_ids=feed_ids)))


@mcp.tool()
def explain_term_tool(phrase: str) -> dict:
    """Map a phrase like best clarity or smooth to ranking weights."""
    return _dump(explain_term(ctx, ExplainTermRequest(phrase=phrase)))


@mcp.tool()
def sanity_check_constraints_tool(feed_ids: List[str]) -> dict:
    """Check decoder constraints for a list of feed IDs."""
    return _dump(sanity_check_constraints(ctx, SanityCheckRequest(feed_ids=feed_ids)))


if __name__ == "__main__":
    # Runs an MCP server over stdio for local IDEs like Cursor
    mcp.run()