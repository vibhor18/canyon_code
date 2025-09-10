from __future__ import annotations
from typing import Dict, Any, List, Tuple
import json, os, pandas as pd
from jsonschema import validate as js_validate
from jsonschema.exceptions import ValidationError
from .models import TableDefRow, FeedRow, EncoderParams, DecoderParams
from util.ranking import clarity_score_from_row


class DataStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        # These will be populated by load_all
        self.table_defs = None
        self.feeds_df = None
        self.encoder_schema = None
        self.decoder_schema = None
        self.encoder_params = None
        self.decoder_params = None
        self.ranking_weights = None

    def _path(self, name: str) -> str:
        return os.path.join(self.data_dir, name)

    def load_all(self) -> None:
        # Load schemas
        with open(self._path("encoder_schema.json"), "r") as f:
            self.encoder_schema = json.load(f)
        with open(self._path("decoder_schema.json"), "r") as f:
            self.decoder_schema = json.load(f)

        # Load params
        with open(self._path("encoder_params.json"), "r") as f:
            enc_raw = json.load(f)
        with open(self._path("decoder_params.json"), "r") as f:
            dec_raw = json.load(f)

        # Validate params against schema if possible
        try:
            js_validate(enc_raw, self.encoder_schema)
        except ValidationError as e:
            print("Warning: encoder params failed schema validation:", e)

        try:
            js_validate(dec_raw, self.decoder_schema)
        except ValidationError as e:
            print("Warning: decoder params failed schema validation:", e)

        # Coerce into models
        self.encoder_params = EncoderParams(**enc_raw)
        self.decoder_params = DecoderParams(**dec_raw)

        # Load table definitions and feeds
        defs_path_csv = self._path("Table_defs_v2.csv")
        feeds_path_csv = self._path("Table_feeds_v2.csv")

        self.table_defs = pd.read_csv(defs_path_csv)
        self.feeds_df = pd.read_csv(feeds_path_csv)

        # Basic normalization
        if "CODEC" in self.feeds_df.columns:
            self.feeds_df["CODEC"] = self.feeds_df["CODEC"].astype(str).str.upper()
        
        for c in ["RES_W", "RES_H", "FRRATE"]:
            if c in self.feeds_df.columns:
                self.feeds_df[c] = pd.to_numeric(self.feeds_df[c], errors="coerce")

        # Sanity checks
        assert self.feeds_df["FEED_ID"].nunique() == len(self.feeds_df), "FEED_ID must be unique"
        assert self.feeds_df["FEED_ID"].isna().sum() == 0, "FEED_ID contains nulls"

    def get_table_schema(self) -> List[TableDefRow]:
        return [TableDefRow(**row._asdict() if hasattr(row, "_asdict") else dict(row))
                for _, row in self.table_defs.iterrows()]

    def list_feeds(self, **filters) -> pd.DataFrame:
        df = self.feeds_df.copy()
        # Supported filters: THEATER contains, min_res_w, min_res_h, min_fps, codec_in list
        theater = filters.get("theater")
        if theater:
            df = df[df["THEATER"].str.contains(theater, case=False, na=False)]
        min_res_w = filters.get("min_res_w")
        if min_res_w is not None:
            df = df[df["RES_W"] >= int(min_res_w)]
        min_res_h = filters.get("min_res_h")
        if min_res_h is not None:
            df = df[df["RES_H"] >= int(min_res_h)]
        min_fps = filters.get("min_fps")
        if min_fps is not None and "FRRATE" in df.columns:
            df = df[df["FRRATE"].astype(float) >= float(min_fps)]
        codec_in = filters.get("codec_in")
        if codec_in:
            codec_upper = [c.upper() for c in codec_in]
            df = df[df["CODEC"].isin(codec_upper)]
        return df

    def clarity_score(self, row) -> float:
        return clarity_score_from_row(row, self.feeds_df, self.ranking_weights or None)

    def filter_and_rank_feeds(self, **filters) -> pd.DataFrame:
        df = self.list_feeds(**filters).copy()
        df["clarity_score"] = df.apply(self.clarity_score, axis=1)
        df = df.sort_values("clarity_score", ascending=False)
        return df

    def get_encoder_params(self) -> EncoderParams:
        return self.encoder_params

    def get_decoder_params(self) -> DecoderParams:
        return self.decoder_params
