from __future__ import annotations
from typing import TypedDict, Optional, Dict, Any, List
import re
from tools_mcp.tools import explain_term, summarize_selection, sanity_check_constraints
from tools_mcp.schemas import ExplainTermRequest, SummarizeSelectionRequest, SanityCheckRequest

from langgraph.graph import StateGraph, END
from tools_mcp.tools import (
    ToolContext, list_feeds, filter_and_rank_feeds,
    get_encoder_params, get_decoder_params
)
from tools_mcp.schemas import (
    ListFeedsRequest, FilterAndRankRequest,
    GetEncoderParamsRequest, GetDecoderParamsRequest,
)

class AgentState(TypedDict, total=False):
    question: str
    intent: str
    filters: Dict[str, Any]
    result: Any
    notes: List[str]
    answer: str
    weights: dict | None
    evidence: dict | None

THEATER_CODES = ["PAC","CONUS","EUR","ME","AFR","ARC"]

def parse_filters(q: str) -> Dict[str, Any]:
    f: Dict[str, Any] = {}
    for code in THEATER_CODES:
        if re.search(rf"\b{code}\b", q, flags=re.IGNORECASE):
            f["theater"] = code
            break
    m = re.search(r"(\d+(?:\.\d+)?)\s*fps", q, flags=re.IGNORECASE)
    if m:
        f["min_fps"] = float(m.group(1))
    m = re.search(r"(\d{3,4})\s*[xX]\s*(\d{3,4})", q)
    if m:
        f["min_res_w"] = int(m.group(1)); f["min_res_h"] = int(m.group(2))
    else:
        m = re.search(r"(\d{3,4})p", q, flags=re.IGNORECASE)
        if m:
            f["min_res_h"] = int(m.group(1))
            f["min_res_w"] = int(int(m.group(1)) * 16 / 9)
    if re.search(r"\b(h265|hevc)\b", q, flags=re.IGNORECASE):
        f["codec_in"] = ["H265","HEVC"]
    if re.search(r"\b(h264|avc)\b", q, flags=re.IGNORECASE):
        f["codec_in"] = ["H264","AVC"]
    if re.search(r"\bav1\b", q, flags=re.IGNORECASE):
        f["codec_in"] = ["AV1"]
    return f

def classify_intent(q: str) -> str:
    q_low = q.lower()
    if "encoder" in q_low:
        return "get_encoder"
    if "decoder" in q_low:
        return "get_decoder"
    if any(k in q_low for k in ["check","validate","compatibility","constraints"]):
        return "sanity_check"
    if any(k in q_low for k in ["list feeds","show feeds","which cameras","which feeds"]):
        return "list_feeds"
    if any(k in q_low for k in ["best clarity","rank","top","best","smooth","latency"]):
        return "rank_feeds"
    return "rank_feeds"

_CTX: Optional[ToolContext] = None
def get_ctx() -> ToolContext:
    global _CTX
    if _CTX is None:
        _CTX = ToolContext(data_dir=".")
    return _CTX

def node_classify(state: AgentState) -> AgentState:
    q = state["question"]
    intent = classify_intent(q)
    filters = parse_filters(q)
    notes = [f"intent={intent}", f"filters={filters}"]
    return {**state, "intent": intent, "filters": filters, "notes": notes}

def node_call_tools(state: AgentState) -> AgentState:
    ctx = get_ctx()
    intent = state["intent"]
    filters = state.get("filters", {})
    qtext = state.get("question", "")

    # get_encoder
    if intent == "get_encoder":
        res = get_encoder_params(ctx, GetEncoderParamsRequest()).params
        return {**state, "result": res}

    # get_decoder
    if intent == "get_decoder":
        res = get_decoder_params(ctx, GetDecoderParamsRequest()).params
        return {**state, "result": res}

    # list_feeds
    if intent == "list_feeds":
        req = ListFeedsRequest(**filters, limit=10)
        res = list_feeds(ctx, req).feeds
        return {**state, "result": res}

    # sanity_check
    if intent == "sanity_check":
        weights = None
        if any(k in qtext.lower() for k in ["clarity", "smooth", "latency"]):
            exp = explain_term(ctx, ExplainTermRequest(phrase=qtext))
            weights = exp.weights
        req_rank = FilterAndRankRequest(**filters, top_k=5, weights=weights)
        ranked = filter_and_rank_feeds(ctx, req_rank).feeds
        ids = [r.FEED_ID for r in ranked]
        issues = sanity_check_constraints(ctx, SanityCheckRequest(feed_ids=ids)).issues
        return {**state, "result": {"ranked": ranked, "issues": issues}, "weights": weights}

    # default: rank_feeds
    weights = None
    if any(k in qtext.lower() for k in ["clarity", "smooth", "latency"]):
        exp = explain_term(ctx, ExplainTermRequest(phrase=qtext))
        weights = exp.weights
    req = FilterAndRankRequest(**filters, top_k=5, weights=weights)
    ranked = filter_and_rank_feeds(ctx, req).feeds
    return {**state, "result": ranked, "weights": weights}

def node_format(state: AgentState) -> AgentState:
    intent = state["intent"]
    res = state.get("result")
    filters = state.get("filters", {})
    weights = state.get("weights")
    lines: List[str] = []
    evidence: dict | None = None

    if intent in ["get_encoder", "get_decoder"]:
        title = "Encoder" if intent == "get_encoder" else "Decoder"
        lines.append(f"{title} parameters:")
        for k, v in res.items():
            lines.append(f"- {k}: {v}")
        evidence = {"params_keys": list(res.keys())[:10]}

    elif intent == "list_feeds":
        header = f"Feeds matching {filters}:" if filters else "Feeds:"
        lines.append(header)
        ids: List[str] = []
        for item in res:
            ids.append(item.FEED_ID)
            lines.append(
                f"- {item.FEED_ID} | {item.THEATER} | {item.RES_W}x{item.RES_H} | {item.FRRATE} fps | {item.CODEC}"
            )
        evidence = {"filters": filters, "feed_ids": ids}

    elif intent == "sanity_check":
        ranked = res.get("ranked", [])
        issues = res.get("issues", [])
        header = f"Top feeds by clarity matching {filters}:" if filters else "Top feeds by clarity:"
        lines.append(header)
        ids: List[str] = []
        scores: List[dict] = []
        for item in ranked:
            ids.append(item.FEED_ID)
            scores.append({"feed_id": item.FEED_ID, "score": float(item.clarity_score)})
            lines.append(
                f"- {item.FEED_ID} | {item.THEATER} | {item.RES_W}x{item.RES_H} | {item.FRRATE} fps | {item.CODEC} | score {item.clarity_score:.3f}"
            )
        if issues:
            lines.append("Constraints findings:")
            for iss in issues:
                lines.append(f"- [{iss.severity}] {iss.feed_id} - {iss.kind}: {iss.detail}")
        else:
            lines.append("No constraint issues found against current decoder caps.")
        evidence = {
            "filters": filters,
            "weights": weights,
            "feed_ids": ids,
            "scores": scores,
            "issues": [iss.model_dump() for iss in issues],
        }

    else:
        # rank_feeds
        header = f"Top feeds by clarity matching {filters}:" if filters else "Top feeds by clarity:"
        lines.append(header)
        ids: List[str] = []
        scores: List[dict] = []
        for item in res:
            ids.append(item.FEED_ID)
            scores.append({"feed_id": item.FEED_ID, "score": float(item.clarity_score)})
            lines.append(
                f"- {item.FEED_ID} | {item.THEATER} | {item.RES_W}x{item.RES_H} | {item.FRRATE} fps | {item.CODEC} | score {item.clarity_score:.3f}"
            )
        evidence = {"filters": filters, "weights": weights, "feed_ids": ids, "scores": scores}

    return {**state, "answer": "\n".join(lines), "evidence": evidence}

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("classify", node_classify)
    g.add_node("call_tools", node_call_tools)
    g.add_node("format", node_format)
    g.set_entry_point("classify")
    g.add_edge("classify", "call_tools")
    g.add_edge("call_tools", "format")   # this edge ensures we format
    g.add_edge("format", END)
    return g.compile()
