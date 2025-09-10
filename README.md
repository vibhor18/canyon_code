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
- Improvement 3: Equivalent run inside a code-gen IDE ✅ instructions for Cursor MCP and Replit below

---

## Project layout

app/
graph.py # LangGraph plan
main.py # FastAPI app - POST /query
datastore/
loader.py # DataStore, schema validation, typed loading
models.py
scripts/
smoke_test.py # Step 1 sanity checks
tool_smoke.py # Call tools without MCP
demo_scenarios.py # Prints 4 demo answers in one run
tools_mcp/
schemas.py # Pydantic request and response models
tools.py # All MCP-style tools
mcp_server.py # Optional MCP stdio server for IDEs
util/
ranking.py # Scoring with configurable weights
data files at repo root:
encoder_schema.json
decoder_schema.json
encoder_params.json
decoder_params.json
Table_defs_v2.csv
Table_feeds_v2.csv

## Quick start

### 1) Environment

Mac or Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


2) Step 1 smoke test
python scripts/smoke_test.py
Expected:
Loaded feeds rows: 100
Unique FEED_ID: 100
Encoder and decoder params printed

3) Tool sanity test
python scripts/tool_smoke.py

4) Run the API
uvicorn app.main:app --reload

Health:
curl -s http://127.0.0.1:8000/health