# Financial Deep Research Agent 🤖📊

> A multi-agent AI system that orchestrates a full LangGraph pipeline — from query routing to investor-grade financial report generation — powered by Gemini 2.5 Flash, Tavily, and yfinance.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Overview

The **Financial Deep Research Agent** is a full-stack AI application that accepts a plain-English financial query (e.g., *"Analyze HDFC Bank's competitive position in Indian private banking"*) and returns a structured, Wall Street–style research report with 10 canonical sections. It rejects non-financial queries at the router stage, classifies the sector, builds a research plan, runs parallelized web searches, reflects on gaps, extracts live market data from Yahoo Finance, cross-references qualitative and quantitative findings, and writes the final report — all in a single API call.

The system solves the core problem of free-tier LLM rate limits by implementing a `GeminiLLMClientRotator` that manages up to 6 Gemini API keys, instantly rotating to the next key on a `429 RESOURCE_EXHAUSTED` error instead of waiting. It is aimed at retail investors, financial analysts, and developers building AI-native fintech tools.

---

## ✨ Features

### Query Routing & Planning
- **Sector Classification Router** — uses `SectorClassification` Pydantic schema to determine if the query is finance-related and classify the sector (IT, Pharma, Banking, etc.) with a confidence score; non-finance queries are rejected immediately with a polite message
- **Structured Research Planner** — generates a `ResearchPlan` with 2 specific tasks across four axes: market overview, competitor analysis, financial metrics, and risk identification

### Iterative Research Loop
- **Concurrent Web Search** — `researcher_node` fires up to 3 parallel Tavily searches per iteration using `asyncio.gather`, collecting raw web findings
- **Reflection Agent** — `reflection_node` evaluates findings against the plan and outputs `ReflectionOutput` with a confidence score, missing information analysis, and up to 3 next search queries; the loop is capped at 1 iteration by design to prevent rate-limit spirals on free tiers

### Quantitative Finance Layer
- **Live yfinance Data** — `finance_node` auto-extracts the ticker symbol via LLM, then fetches current price, market cap, income statements, balance sheet, and cash flow from Yahoo Finance
- **Computed Metrics** — `calculations.py` computes 50-day and 200-day SMAs from historical price data; `calculate_yoy_growth` computes year-over-year revenue growth from the income statement
- **Key Ratios** — `ratios.py` extracts Trailing PE, Forward PE, PEG Ratio, Price-to-Book, Debt-to-Equity, ROE, Profit Margin, Operating Margin, and EBITDA directly from yfinance's `info` dict

### Analysis & Reporting
- **Analyst Node** — cross-references qualitative web findings with hard quantitative numbers, explicitly flagging discrepancies between the web narrative and the financial data
- **Reporter Node** — synthesizes all context into a 10-section Markdown report (Executive Summary → Sources) following a strict Wall Street analyst prompt; explicitly instructs the LLM to write "Data not available" rather than hallucinate

### RAG / Document Intelligence
- **PDF Ingestion** — users can upload 10-Ks and Annual Reports via the Streamlit sidebar; `pdf_parser.py` chunks the document and `vectorstore.py` stores embeddings in a local ChromaDB instance under `chroma_db/`
- **Local Embeddings** — uses `all-MiniLM-L6-v2` via `HuggingFaceEmbeddings` as a singleton to avoid repeated model loads; runs entirely locally with no additional API calls

### API Key Rotation
- **`GeminiLLMClientRotator`** — a smart singleton LLM client that accepts up to 6 `GOOGLE_API_KEY_*` values, tries them in priority order (Key 1 always preferred), marks a key as exhausted for 60 seconds on a 429 error, and picks up from the exact retry-delay hint embedded in the error message

### Frontend
- **Streamlit Chat UI** (`frontend/app.py`) — a wide-layout chat interface with a sidebar for optional ticker input, a PDF upload + ChromaDB ingestion button, a backend health indicator, and a persistent `st.session_state` chat history

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| FastAPI 0.115+ | REST API framework; hosts `/api/v1/research/` and `/api/v1/documents/upload` |
| Uvicorn | ASGI server to run the FastAPI app |
| LangGraph 0.2+ | Directed graph runtime for multi-agent state orchestration |
| LangChain Core 0.3+ | Message types, structured output, and tool interfaces |
| `langchain-google-genai` | Gemini 2.5 Flash client with structured output support |
| `tavily-python` | Web search API with per-result title, URL, and content |
| yfinance 0.2.37 | Live and historical market data from Yahoo Finance |
| Pydantic 2.6 | Typed state schemas, structured LLM output validation |
| `pydantic-settings` | `.env` file loading into the `Settings` config object |
| Tenacity | Retry logic utilities |

### Frontend

| Technology | Purpose |
|---|---|
| Streamlit 1.32 | Chat UI with sidebar controls and `st.session_state` history |
| Requests | HTTP client to call the FastAPI backend |

### AI & Embeddings

| Technology | Purpose |
|---|---|
| Gemini 2.5 Flash (`gemini-2.5-flash`) | All LLM inference — planning, reflection, analysis, reporting |
| `all-MiniLM-L6-v2` (HuggingFace) | Local sentence embeddings for RAG document chunks |
| ChromaDB | Local vector store for PDF-ingested financial documents |

### Dev Tooling

| Technology | Purpose |
|---|---|
| python-dotenv | Local `.env` loading for development |
| logging | Structured INFO/ERROR logs throughout all agent nodes |
| asyncio | Concurrent search execution inside `researcher_node` and `fast_research` |

---

## 🏗️ Architecture / How It Works

```
User Query (via Streamlit or REST)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  POST /api/v1/research/  →  run_fast_research()          │
│         OR                                               │
│  LangGraph Graph  →  create_research_graph()             │
└───────────────────────────┬─────────────────────────────┘
                            │
          ┌─────────────────▼──────────────────┐
          │       LangGraph StateGraph          │
          │  (ResearchState typed dict)          │
          └─────────────────────────────────────┘
                            │
               ┌────────────▼────────────┐
               │  1. router_node          │  ← Gemini: SectorClassification
               │  (Rejected → END)        │
               └────────────┬────────────┘
                            │ finance query
               ┌────────────▼────────────┐
               │  2. planner_node         │  ← Gemini: ResearchPlan
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │  3. researcher_node      │  ← Tavily: 3 concurrent searches
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │  4. reflection_node      │  ← Gemini: ReflectionOutput
               │  (loop back if gaps      │    confidence < 1.0 AND iter < 1
               │   OR proceed to finance) │
               └────────────┬────────────┘
                            │ is_sufficient OR iter >= 1
               ┌────────────▼────────────┐
               │  5. finance_node         │  ← yfinance: price, ratios, SMAs,
               │                          │    YoY revenue growth
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │  6. analyst_node         │  ← Gemini: cross-reference memo
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │  7. reporter_node        │  ← Gemini: 10-section Markdown report
               └────────────┬────────────┘
                            │
                      final_report string
                            │
               ┌────────────▼────────────┐
               │  ResearchResponse JSON   │
               │  → Streamlit renders     │
               │    Markdown in chat      │
               └─────────────────────────┘
```

**Parallel fast path:** `run_fast_research()` in `services/fast_research.py` is the production path used by the `/api/v1/research/` route. It makes exactly 2 Gemini calls (brainstorm + master analyst) and 4 concurrent Tavily searches, bypassing the full LangGraph graph for speed.

**Key rotation flow:** Every `ainvoke` or `ainvoke_structured` call on `gemini_client` goes through `GeminiLLMClientRotator._get_next_client()`, which scans the in-memory `_exhausted_until` dict and instantly picks the first available key. On a `429`, the key is marked exhausted using the delay extracted from the error message itself (via regex on `retry_in: Xs`).

---

## 📂 Folder Structure

```
Ai-orchestration-agent--main/
│
├── backend/
│   ├── .env.example                  # Template for all required environment variables
│   ├── requirements.txt              # All Python dependencies
│   ├── frontend.py                   # Alternate Streamlit launcher from within backend/
│   │
│   ├── app/
│   │   ├── main.py                   # FastAPI app factory; registers all routers
│   │   ├── core/
│   │   │   └── config.py             # Pydantic Settings — loads .env.dev into settings object
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py            # ResearchRequest, ResearchResponse, DocumentUploadResponse
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py         # GET /health/ — liveness probe
│   │   │       ├── research.py       # POST /api/v1/research/ — main research trigger
│   │   │       └── documents.py      # POST /api/v1/documents/upload — PDF ingestion
│   │   │
│   │   ├── graph/
│   │   │   ├── workflow.py           # LangGraph StateGraph definition + compiled research_graph
│   │   │   └── nodes.py              # Thin shim that re-exports all agent node callables
│   │   │
│   │   ├── state/
│   │   │   └── research_state.py     # ResearchState TypedDict — single source of truth for graph state
│   │   │
│   │   ├── agents/
│   │   │   ├── shared/
│   │   │   │   └── llm.py            # GeminiLLMClientRotator singleton (gemini_client)
│   │   │   ├── planner/
│   │   │   │   └── planner.py        # planner_node — generates 8-task ResearchPlan
│   │   │   ├── router/
│   │   │   │   └── sector_router.py  # router_node — classifies sector or rejects query
│   │   │   ├── researcher/
│   │   │   │   ├── researcher.py     # researcher_node — concurrent Tavily search + synthesis
│   │   │   │   └── reflection.py     # reflection_node — gap analysis + next query generation
│   │   │   ├── reporter/
│   │   │   │   └── reporter.py       # reporter_node — 10-section final report writer
│   │   │   └── nodes/
│   │   │       ├── finance.py        # finance_node — ticker extraction + yfinance data pull
│   │   │       └── analyst.py        # analyst_node — qualitative vs quantitative cross-reference
│   │   │
│   │   ├── services/
│   │   │   ├── fast_research.py      # 2-call fast pipeline (production path for /research/)
│   │   │   ├── finance.py            # Helper finance service utilities
│   │   │   ├── gemini.py             # Standalone Gemini service wrapper
│   │   │   ├── tavily_search.py      # Tavily service wrapper
│   │   │   └── vectordb.py           # Vector DB service helper
│   │   │
│   │   └── tools/
│   │       ├── finance/
│   │       │   ├── market_data.py    # get_company_info, get_historical_prices, get_financial_statements
│   │       │   ├── calculations.py   # calculate_moving_averages (SMA50/200), calculate_yoy_growth
│   │       │   └── ratios.py         # extract_key_ratios (PE, PEG, ROE, margins, EBITDA)
│   │       ├── rag/
│   │       │   ├── pdf_parser.py     # Parses + chunks PDF files for ingestion
│   │       │   ├── embeddings.py     # Singleton all-MiniLM-L6-v2 local embeddings
│   │       │   ├── vectorstore.py    # ChromaDB singleton — persists to ./chroma_db/
│   │       │   └── retriever.py      # RAG retriever over the vectorstore
│   │       └── search/
│   │           └── tavily_search.py  # TavilySearchTool wrapper with .search() method
│   │
│   └── test_*.py                     # 15+ test scripts covering graph, API, finance, RAG, Gemini
│
└── frontend/
    └── app.py                        # Streamlit chat UI — connects to FastAPI backend
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.11+
- A [Google AI Studio](https://aistudio.google.com/) account (free tier works; up to 6 API keys supported)
- A [Tavily](https://tavily.com/) API key (free tier: 1,000 searches/month)

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/Ai-orchestration-agent.git
cd Ai-orchestration-agent
```

### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

> **Note:** `pydantic` is pinned at `2.6.3` in `requirements.txt`; the `>=2.9.0` line is overridden. If you encounter Pydantic version conflicts, install with `pip install pydantic==2.6.3 --force-reinstall`.

### 4. Configure Environment Variables
```bash
cp .env.example .env.dev
```

Open `.env.dev` and fill in your keys (see [Environment Variables](#-environment-variables) below).

### 5. Run the Backend
```bash
# From within the backend/ directory
uvicorn app.main:app --reload --port 8001
```

The API will be available at `http://127.0.0.1:8001`. Visit `http://127.0.0.1:8001/docs` for the interactive Swagger UI.

### 6. Run the Frontend
```bash
# In a separate terminal, from the project root
streamlit run frontend/app.py
```

The Streamlit UI will open at `http://localhost:8501`.

### 7. Verify the Connection
The Streamlit sidebar displays a green **✅ Backend: Online** badge when the FastAPI health endpoint responds successfully.

---

## 🔑 Environment Variables

All variables are loaded from `backend/.env.dev` via `pydantic-settings`.

| Variable | Description | Example |
|---|---|---|
| `GOOGLE_API_KEY` | Primary Gemini API key (Key 1 — always tried first) | `AIzaSy...` |
| `GOOGLE_API_KEY_2` | Fallback Gemini key — used when Key 1 hits quota | `AIzaSy...` |
| `GOOGLE_API_KEY_3` | Third Gemini key in the rotation pool | `AIzaSy...` |
| `GOOGLE_API_KEY_4` | Fourth Gemini key | `AIzaSy...` |
| `GOOGLE_API_KEY_5` | Fifth Gemini key | `AIzaSy...` |
| `GOOGLE_API_KEY_6` | Sixth Gemini key (max rotation depth) | `AIzaSy...` |
| `TAVILY_API_KEY` | Tavily web search API key | `tvly-...` |
| `ENVIRONMENT` | App environment flag | `development` |
| `LOG_LEVEL` | Python logging verbosity | `info` |

> You only need `GOOGLE_API_KEY` and `TAVILY_API_KEY` to get started. Additional `GOOGLE_API_KEY_*` entries increase throughput on free-tier quotas.

---

## 🧪 Usage

### Via the Streamlit Chat UI

1. Open `http://localhost:8501`
2. (Optional) Enter a stock ticker in the sidebar (e.g., `AAPL`, `HDFCBANK.NS`). Leave blank to let the AI auto-detect it from your query.
3. Type a financial query in the chat input, for example:
   - `"Provide a comprehensive analysis of Infosys's position in the IT services market"`
   - `"What is the investment outlook for Tesla in 2025?"`
   - `"Analyze HDFC silver ETF"`
4. Wait 30–90 seconds (longer on free API tier) while the pipeline runs. A status indicator shows `Planner → Researcher → Analyst → Reporter`.
5. The 10-section Markdown report renders inline in the chat.

### Via the RAG Knowledge Base (PDF Upload)
1. In the sidebar, upload a PDF Annual Report or 10-K.
2. Enter the stock ticker in the ticker field (required for metadata tagging in ChromaDB).
3. Click **Ingest into Local Vector DB** — the system chunks the PDF, embeds it with `all-MiniLM-L6-v2`, and stores it in `backend/chroma_db/`.
4. Subsequent research queries can use this document as a retrieval source (wired via `retrieved_documents` in `ResearchState`).

### Via the REST API
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/research/" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze Apple competitive moat", "company_symbol": "AAPL"}'
```

Response:
```json
{
  "status": "completed",
  "final_report": "# Apple Inc. - Comprehensive Research Report\n\n## 1. Executive Summary\n..."
}
```

---

## 📸 Screenshots / Demo

| View | Screenshot |
|---|---|
| Streamlit Chat Interface | *(add `screenshots/chat_ui.png`)* |
| Research Report Output | *(add `screenshots/report_output.png`)* |
| Sidebar – PDF Upload | *(add `screenshots/sidebar_upload.png`)* |
| FastAPI Swagger Docs | *(add `screenshots/swagger_docs.png`)* |

> To capture: run the app, ask a query like "Analyze TSLA", and screenshot the rendered Markdown report.

---

## 🚧 Challenges & Learnings

**1. Free-Tier Rate Limits on Gemini Flash**
The system makes 5–7 Gemini calls per full LangGraph pipeline run (router → planner → researcher synthesis → reflection → analyst → reporter). On free tier, `429 RESOURCE_EXHAUSTED` errors happen within 2–3 consecutive queries. The solution was `GeminiLLMClientRotator` — it reads the `retry_in: Xs` value embedded in the error string via regex and sets the exhaustion timer to exactly that duration plus a 5-second buffer, rather than a naive flat 60-second backoff. This eliminated most unnecessary wait time.

**2. Infinite Research Loop Risk**
The initial LangGraph reflection loop design had no hard ceiling, meaning a low-confidence reflection could spin indefinitely if Tavily searches kept returning shallow results. The fix in `workflow.py` (`route_after_reflection`) caps `iteration_count >= 1`, forcing the graph to proceed to the finance node after at most one researcher-reflection cycle. This is documented inline as `# PERFORMANCE FIX`.

**3. Gemini Structured Output Content Blocks**
`ChatGoogleGenerativeAI.ainvoke()` returns a `BaseMessage` whose `.content` field can be either a plain string or a list of content dicts (e.g., `[{"type": "text", "text": "..."}]`). Several agent nodes (`researcher.py`, `analyst.py`) include explicit list-flattening guards to handle both formats, preventing silent `AttributeError` crashes in production.

**4. yfinance on Non-US Tickers**
Indian exchange tickers (e.g., `HDFCBANK.NS`) require the `.NS` suffix for NSE or `.BO` for BSE. The ticker extraction LLM prompt does not currently enforce this suffix for Indian stocks, meaning `finance_node` may silently return empty data for Indian queries. The `get_company_info` and `extract_key_ratios` functions log the error but return empty dicts rather than raising, so the pipeline gracefully degrades to qualitative-only reports.

**5. ChromaDB Persistence Path Resolution**
`VectorStoreManager` resolves `CHROMA_PERSIST_DIR` using `os.getcwd()` at import time, which means the resolved path depends on which directory Uvicorn is launched from. If Uvicorn is started from the project root rather than `backend/`, the `chroma_db/` directory ends up in the wrong location. This is a subtle operational footgun that surfaces only when re-ingesting documents across restarts.

---

## 🔮 Future Improvements

**1. Indian Ticker Auto-Suffix**
Extend the `TickerExtraction` Pydantic schema in `finance_node` to include an `exchange` field, and append `.NS` or `.BO` automatically when the sector classification identifies Indian stocks. This directly addresses the silent yfinance data gaps for NIFTY/BSE-listed companies.

**2. RAG Integration into the Research Graph**
`ResearchState` already includes a `retrieved_documents` field annotated for accumulation, but no node currently reads from ChromaDB during graph execution. Wiring `tools/rag/retriever.py` into `researcher_node` would allow uploaded 10-Ks to supplement Tavily search results.

**3. Streaming Report Output**
The current frontend polls a single blocking `requests.post()` with a 300-second timeout. Replacing `gemini_client.ainvoke()` in `reporter_node` with `astream()` and adding a FastAPI `StreamingResponse` endpoint would allow the Streamlit UI to display the report token-by-token, dramatically improving perceived latency.

**4. LangGraph Persistence / Checkpointing**
LangGraph supports checkpointing via `SqliteSaver` or `PostgresSaver`. Adding a checkpointer to `create_research_graph()` would allow interrupted pipelines to resume from the last completed node rather than restarting from scratch — useful for multi-step queries on slow API tiers.

**5. OpenAI / Other LLM Backends**
`langchain-openai` is already in `requirements.txt` and `AgentState` in `state.py` references a generic `messages` field. Abstracting `gemini_client` behind a `BaseLLMClient` interface would enable swapping to GPT-4o or Claude with a single config change.

**6. Structured Report Export**
The `final_report` is currently a raw Markdown string. Adding a `/api/v1/research/export` endpoint that converts the Markdown to PDF using `weasyprint` or `reportlab` would produce shareable investor-grade documents without copy-pasting from the chat UI.

**7. Test Coverage with Async Fixtures**
The 15+ test files in `backend/` are standalone scripts rather than a proper `pytest` suite. Migrating them to `pytest-asyncio` with shared fixtures for `gemini_client` mocking and `test_client` from FastAPI's `TestClient` would enable CI integration and faster local development feedback.

---

## 🤝 Contributing

1. Fork the repository and create a branch: `git checkout -b feat/your-feature`
2. Make your changes; follow existing module patterns (each agent node is an `async def node(state: ResearchState) -> Dict[str, Any]`)
3. Commit with conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`
4. Open a pull request with a description of what the change does and which agent node it affects

**Code style requirements:**
- Python 3.11+ type hints throughout; Pydantic models for all LLM structured outputs
- All LLM calls must go through `gemini_client` (the `GeminiLLMClientRotator` singleton) — never instantiate `ChatGoogleGenerativeAI` directly in agent nodes
- Use `logger = logging.getLogger(__name__)` in every module; log at INFO for pipeline milestones, ERROR for exceptions
- Agent node functions must be `async def` and return a partial `ResearchState` dict

**Good first issues:**
- Add `.NS`/`.BO` suffix detection for Indian tickers in `finance_node`
- Fix `CHROMA_PERSIST_DIR` to use an absolute path relative to `__file__` instead of `os.getcwd()`
- Add a `pytest` test for `GeminiLLMClientRotator` key rotation logic using mocked `ChatGoogleGenerativeAI` clients

---

## 📜 License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
