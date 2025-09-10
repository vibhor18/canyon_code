from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class TableDefRow(BaseModel):
    header: str
    type: str
    allowed_values: Optional[str] = None
    description: Optional[str] = None

class FeedRow(BaseModel):
    FEED_ID: int
    THEATER: Optional[str] = None
    FRRATE: Optional[float] = None
    RES_W: Optional[int] = None
    RES_H: Optional[int] = None
    CODEC: Optional[str] = None

class EncoderParams(BaseModel):
    codec: Literal["H264","H265","AV1","VP9","MPEG2","MPEG4","VC1","HEVC","AVC","VVC","EVC","LCAV","OTHER"] | str
    profile: Optional[str] = None
    level: Optional[str] = None
    bit_depth: Optional[int] = None
    framerate: Optional[float] = None
    gop_size: Optional[int] = None
    rc_mode: Optional[str] = None
    timestamp_mode: Optional[str] = None
    bitrate_kbps: Optional[int] = None
    maxrate_kbps: Optional[int] = None
    vbv_buf_ms: Optional[int] = None
    b_frames: Optional[int] = None
    ref_frames: Optional[int] = None
    chroma: Optional[str] = None
    color_primaries: Optional[str] = None
    transfer_characteristics: Optional[str] = None
    matrix_coeffs: Optional[str] = None
    tune: Optional[str] = None
    preset: Optional[str] = None
    psy_rd: Optional[float] = None
    aq_mode: Optional[str] = None
    keyint_min: Optional[int] = None
    scene_cut: Optional[bool] = None
    lookahead: Optional[int] = None

class DecoderParams(BaseModel):
    max_threads: Optional[int] = None
    dpb_size: Optional[int] = None
    reorder_frames: Optional[bool] = None
    jitter_buf_ms: Optional[int] = None
    av_sync: Optional[str] = None
    output_format: Optional[str] = None
    deinterlace: Optional[str] = None
    cap_max_res_w: Optional[int] = None
    cap_max_res_h: Optional[int] = None
    color_space: Optional[str] = None
    chroma_format: Optional[str] = None
    skip_nonref: Optional[bool] = None
    deblock: Optional[bool] = None
    sao: Optional[bool] = None
