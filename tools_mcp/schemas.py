from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel

class GetTableSchemaRequest(BaseModel):
    pass

class TableColumn(BaseModel):
    header: str
    type: str
    allowed_values: Optional[str] = None
    description: Optional[str] = None

class GetTableSchemaResponse(BaseModel):
    columns: List[TableColumn]

class ListFeedsRequest(BaseModel):
    theater: Optional[str] = None
    min_res_w: Optional[int] = None
    min_res_h: Optional[int] = None
    min_fps: Optional[float] = None
    codec_in: Optional[List[str]] = None
    limit: Optional[int] = 50

class FeedItem(BaseModel):
    FEED_ID: str
    THEATER: Optional[str] = None
    RES_W: Optional[int] = None
    RES_H: Optional[int] = None
    FRRATE: Optional[float] = None
    CODEC: Optional[str] = None

class ListFeedsResponse(BaseModel):
    feeds: List[FeedItem]

class FilterAndRankRequest(BaseModel):
    theater: Optional[str] = None
    min_res_w: Optional[int] = None
    min_res_h: Optional[int] = None
    min_fps: Optional[float] = None
    codec_in: Optional[List[str]] = None
    sort_by: Literal["clarity"] = "clarity"
    top_k: Optional[int] = 10
    weights: Optional[Dict[str, float]] = None

class RankedFeedItem(FeedItem):
    clarity_score: float

class FilterAndRankResponse(BaseModel):
    feeds: List[RankedFeedItem]

class GetEncoderParamsRequest(BaseModel):
    pass

class GetDecoderParamsRequest(BaseModel):
    pass

class GetParamsResponse(BaseModel):
    params: Dict[str, Any]

class SummarizeSelectionRequest(BaseModel):
    feed_ids: List[str]

class SummaryRow(BaseModel):
    FEED_ID: str
    THEATER: Optional[str]
    RES_W: Optional[int]
    RES_H: Optional[int]
    FRRATE: Optional[float]
    CODEC: Optional[str]
    clarity_score: Optional[float] = None

class SummarizeSelectionResponse(BaseModel):
    rows: List[SummaryRow]

class ExplainTermRequest(BaseModel):
    phrase: str

class ExplainTermResponse(BaseModel):
    intent: str
    weights: Dict[str, float]  # keys: resolution, fps, codec
    notes: List[str] = []

class SanityCheckRequest(BaseModel):
    feed_ids: List[str]

class ConstraintIssue(BaseModel):
    feed_id: str
    kind: str
    detail: str
    severity: Literal["warn", "error"] = "warn"

class SanityCheckResponse(BaseModel):
    issues: List[ConstraintIssue]
