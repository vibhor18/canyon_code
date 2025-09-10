# Canyon Code - Agentic Query System

Natural language agent that answers questions about camera feeds, encoder parameters, and decoder parameters.

Built with:
- Typed DataStore for CSV and JSON inputs
- MCP tools for all data operations
- LangGraph plan that always calls tools
- FastAPI endpoint that returns answer plus evidence
- Zero LLM usage by default to keep cost near zero

---

## What this repo delivers

- Base: NL query app for feeds, encoder, decoder ✅
- Improvement 1: LangGraph for orchestration ✅
- Improvement 2: Data operations as MCP tools ✅
- Improvement 3: Equivalent run inside a code-gen IDE ✅ Cursor MCP instructions included

---

## Project layout

\`\`\`text
canyoncode_agent_step1_scaffold/
├─ app/
│  ├─ graph.py               # LangGraph plan
│  └─ main.py                # FastAPI app, POST /query
├─ datastore/
│  ├─ loader.py              # DataStore, schema validation, typed loading
│  └─ models.py
├─ scripts/
│  ├─ smoke_test.py          # Step 1 sanity checks
│  ├─ tool_smoke.py          # Call tools without MCP
│  └─ demo_scenarios.py      # Prints 4 demo answers in one run
├─ tools_mcp/
│  ├─ schemas.py             # Pydantic request and response models
│  ├─ tools.py               # MCP-style tools
│  └─ mcp_server.py          # MCP stdio server for IDEs like Cursor
├─ util/
│  └─ ranking.py             # Scoring with configurable weights
├─ encoder_schema.json
├─ decoder_schema.json
├─ encoder_params.json
├─ decoder_params.json
├─ Table_defs_v2.csv
└─ Table_feeds_v2.csv
\`\`\`

---

## Quick start

### 1) Environment

macOS or Linux:
\`\`\`bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
\`\`\`


### 2) Smoke test

\`\`\`bash
python scripts/smoke_test.py
\`\`\`

Expected:
- Loaded feeds rows: 100
- Unique FEED_ID: 100
- Encoder and decoder params printed

### 3) Tool sanity test

\`\`\`bash
python scripts/tool_smoke.py
\`\`\`

### 4) Run the API

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

Health:
\`\`\`bash
curl -s http://127.0.0.1:8000/health
\`\`\`

---

## Demo queries

Run these in a second terminal while the server is running.

1) Ranking with clarity
\`\`\`bash
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"question":"Top 5 feeds with best clarity in PAC"}' | jq
\`\`\`

2) Filtered listing
\`\`\`bash
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"question":"List feeds at least 1080p and 30 fps using H265 in EUR"}' | jq
\`\`\`

3) Parameters introspection
\`\`\`bash
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"question":"Show decoder parameters"}' | jq
\`\`\`

4) Constraint check
\`\`\`bash
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"question":"Check top feeds in PAC for constraints"}' | jq
\`\`\`

Optional smoothness demo:
\`\`\`bash
curl -s -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" \
  -d '{"question":"Top 5 feeds with smooth video in CONUS"}' | jq
\`\`\`

---

## API reference

- POST /query

Request:
\`\`\`json
{"question":"Top 5 feeds with best clarity in PAC"}
\`\`\`

Response:
\`\`\`json
{
  "answer": "Top feeds by clarity matching {...}\n- FD-... | ...",
  "evidence": {
    "filters": {"theater":"PAC"},
    "weights": {"resolution":0.6,"fps":0.2,"codec":0.2},
    "feed_ids": ["FD-...","FD-..."],
    "scores": [{"feed_id":"FD-...","score":1.0}]
  }
}
\`\`\`

- GET /health returns {"status":"ok"}

---

## Cursor MCP (code-gen IDE)

Use tools inside Cursor via MCP.

### project config file

Create \`.cursor/mcp.json\` in the repo root with paths:

\`\`\`json
{
  "mcpServers": {
    "canyoncode-tools": {
      "command": "$PY",
      "args": ["-m", "tools_mcp.mcp_server"],
      "cwd": "$PROJ"
    }
  }
}
\`\`\`

Restart Cursor. In the MCP Tools panel you should see:
- get_table_schema_tool
- list_feeds_tool
- filter_and_rank_tool
- get_encoder_params_tool
- get_decoder_params_tool
- summarize_selection_tool
- explain_term_tool
- sanity_check_constraints_tool

Example tool inputs in Cursor chat:
\`\`\`json
{"theater":"PAC","limit":3}
\`\`\`

\`\`\`json
{"theater":"EUR","top_k":5}
\`\`\`

\`\`\`json
{}
\`\`\`

\`\`\`json
{"phrase":"best clarity"}
\`\`\`

\`\`\`json
{"feed_ids":["FD-LLF3SB","FD-8D150S"]}
\`\`\`

---

## Tests

Minimal pytest examples in \`tests/test_basic.py\`:

\`\`\`bash
pip install pytest
pytest -q
\`\`\`

---

## How it works

- DataStore loads CSV and JSON, validates against the provided schemas, normalizes types.
- MCP tools provide a narrow surface: list, rank, params, summarize, explain term, sanity check.
- LangGraph parses intent and filters, optionally uses explain_term to set weights for clarity and smooth, then calls tools and formats the answer.
- FastAPI exposes POST /query that returns answer plus evidence for traceability.

---

## Assumptions and limits

- FEED_ID is unique
- FRRATE is frames per second
- RES_W and RES_H are pixel counts
- CODEC values normalized to upper case
- Clarity score combines resolution, frame rate, and a codec bonus
- Constraint checker uses decoder caps and a conservative codec allowlist
- Latency mapping is a placeholder weight shift

---


