from __future__ import annotations
from typing import List,Dict, Any
from .schemas import ExplainTermRequest, ExplainTermResponse
import pandas as pd
import re
from datastore.loader import DataStore
from .schemas import (
    GetTableSchemaRequest, GetTableSchemaResponse, TableColumn,
    ListFeedsRequest, ListFeedsResponse, FeedItem,
    FilterAndRankRequest, FilterAndRankResponse, RankedFeedItem,
    GetEncoderParamsRequest, GetDecoderParamsRequest, GetParamsResponse,
    SummarizeSelectionRequest, SummarizeSelectionResponse, SummaryRow
)
from .schemas import SanityCheckRequest, SanityCheckResponse, ConstraintIssue


class ToolContext:
    def __init__(self, data_dir: str = "."):
        self.store = DataStore(data_dir)
        self.store.load_all()

def get_table_schema(ctx: ToolContext, req: GetTableSchemaRequest) -> GetTableSchemaResponse:
    cols = []
    for _, row in ctx.store.table_defs.iterrows():
        cols.append(TableColumn(
            header=str(row.get("header")),
            type=str(row.get("type")),
            allowed_values=row.get("allowed_values"),
            description=row.get("description"),
        ))
    return GetTableSchemaResponse(columns=cols)

def list_feeds(ctx: ToolContext, req: ListFeedsRequest) -> ListFeedsResponse:
    df = ctx.store.list_feeds(
        theater=req.theater,
        min_res_w=req.min_res_w,
        min_res_h=req.min_res_h,
        min_fps=req.min_fps,
        codec_in=req.codec_in,
    )
    if req.limit is not None:
        df = df.head(req.limit)
    feeds = [
        FeedItem(
            FEED_ID=str(r.FEED_ID),
            THEATER=r.THEATER if "THEATER" in df.columns else None,
            RES_W=int(r.RES_W) if pd.notna(r.RES_W) else None,
            RES_H=int(r.RES_H) if pd.notna(r.RES_H) else None,
            FRRATE=float(r.FRRATE) if "FRRATE" in df.columns and pd.notna(r.FRRATE) else None,
            CODEC=str(r.CODEC) if "CODEC" in df.columns else None,
        )
        for r in df.itertuples(index=False)
    ]
    return ListFeedsResponse(feeds=feeds)

def filter_and_rank_feeds(ctx: ToolContext, req: FilterAndRankRequest) -> FilterAndRankResponse:
    if not hasattr(ctx.store, "ranking_weights"):
        ctx.store.ranking_weights = None

    old = ctx.store.ranking_weights
    try:
        # Temporarily apply custom weights for this request
        if req.weights:
            ctx.store.ranking_weights = req.weights

        df = ctx.store.filter_and_rank_feeds(
            theater=req.theater,
            min_res_w=req.min_res_w,
            min_res_h=req.min_res_h,
            min_fps=req.min_fps,
            codec_in=req.codec_in,
        )

        if req.top_k is not None:
            df = df.head(req.top_k)

        feeds = [
            RankedFeedItem(
                FEED_ID=str(r.FEED_ID),
                THEATER=r.THEATER if "THEATER" in df.columns else None,
                RES_W=int(r.RES_W) if pd.notna(r.RES_W) else None,
                RES_H=int(r.RES_H) if pd.notna(r.RES_H) else None,
                FRRATE=float(r.FRRATE) if "FRRATE" in df.columns and pd.notna(r.FRRATE) else None,
                CODEC=str(r.CODEC) if "CODEC" in df.columns else None,
                clarity_score=float(r.clarity_score),
            )
            for r in df.itertuples(index=False)
        ]

        return FilterAndRankResponse(feeds=feeds)
    finally:
        # Always restore previous weights
        ctx.store.ranking_weights = old

def get_encoder_params(ctx: ToolContext, req: GetEncoderParamsRequest) -> GetParamsResponse:
    return GetParamsResponse(params=ctx.store.get_encoder_params().model_dump())

def get_decoder_params(ctx: ToolContext, req: GetDecoderParamsRequest) -> GetParamsResponse:
    return GetParamsResponse(params=ctx.store.get_decoder_params().model_dump())

def summarize_selection(ctx: ToolContext, req: SummarizeSelectionRequest) -> SummarizeSelectionResponse:
    subset = ctx.store.feeds_df[ctx.store.feeds_df["FEED_ID"].astype(str).isin(req.feed_ids)].copy()
    if "clarity_score" not in subset.columns:
        subset["clarity_score"] = subset.apply(ctx.store.clarity_score, axis=1)
    rows = [
        SummaryRow(
            FEED_ID=str(r.FEED_ID),
            THEATER=r.THEATER if "THEATER" in subset.columns else None,
            RES_W=int(r.RES_W) if pd.notna(r.RES_W) else None,
            RES_H=int(r.RES_H) if pd.notna(r.RES_H) else None,
            FRRATE=float(r.FRRATE) if "FRRATE" in subset.columns and pd.notna(r.FRRATE) else None,
            CODEC=str(r.CODEC) if "CODEC" in subset.columns else None,
            clarity_score=float(r.clarity_score) if pd.notna(r.clarity_score) else None,
        )
        for r in subset.itertuples(index=False)
    ]
    return SummarizeSelectionResponse(rows=rows)

def explain_term(ctx: ToolContext, req: ExplainTermRequest) -> ExplainTermResponse:
    p = req.phrase.lower()
    notes = []
    # defaults
    weights = {"resolution": 0.5, "fps": 0.3, "codec": 0.2}
    intent = "rank_feeds"
    if "clarity" in p or "sharp" in p or "detail" in p:
        weights = {"resolution": 0.6, "fps": 0.2, "codec": 0.2}
        notes.append("clarity -> resolution heavy, then codec, some fps")
    elif "smooth" in p or "fluid" in p:
        weights = {"resolution": 0.3, "fps": 0.6, "codec": 0.1}
        notes.append("smooth -> fps heavy")
    elif "low latency" in p or "latency" in p:
        # we still use clarity score but hint that fps and codec matter for fluid decode
        weights = {"resolution": 0.2, "fps": 0.6, "codec": 0.2}
        notes.append("latency -> fps heavy placeholder")
    return ExplainTermResponse(intent=intent, weights=weights, notes=notes)


def sanity_check_constraints(ctx: ToolContext, req: SanityCheckRequest) -> SanityCheckResponse:
    df = ctx.store.feeds_df.copy()
    sub = df[df["FEED_ID"].astype(str).isin(req.feed_ids)]
    dec = ctx.store.get_decoder_params().model_dump()
    cap_w = dec.get("cap_max_res_w") or 10**9
    cap_h = dec.get("cap_max_res_h") or 10**9

    issues: List[ConstraintIssue] = []
    for r in sub.itertuples(index=False):
        fid = str(r.FEED_ID)

        # resolution ceiling
        if r.RES_W and r.RES_H and (r.RES_W > cap_w or r.RES_H > cap_h):
            issues.append(ConstraintIssue(
                feed_id=fid,
                kind="resolution_cap",
                detail=f"{r.RES_W}x{r.RES_H} exceeds decoder cap {cap_w}x{cap_h}",
                severity="error",
            ))

        # conservative codec allowlist
        codec = str(getattr(r, "CODEC", "") or "").upper()
        allowed = {"H265","HEVC","H264","AVC"}
        if codec and codec not in allowed:
            issues.append(ConstraintIssue(
                feed_id=fid,
                kind="codec_unknown",
                detail=f"Codec {codec} not in allowlist {sorted(list(allowed))}. Verify support.",
                severity="warn",
            ))

        # high fps warning
        fps = float(getattr(r, "FRRATE", 0) or 0)
        if fps > 60:
            issues.append(ConstraintIssue(
                feed_id=fid,
                kind="fps_high",
                detail=f"{fps} fps may require tighter jitter buffer or reorder settings.",
                severity="warn",
            ))

    return SanityCheckResponse(issues=issues)