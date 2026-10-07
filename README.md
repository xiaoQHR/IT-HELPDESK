# IT Helpdesk

IT Helpdesk is a multi-agent assistant for internal IT support. It classifies employee requests, routes them to a specialized agent, retrieves internal knowledge, remembers conversation context, and escalates high-risk issues for human follow-up.

The current implementation focuses on a testable vertical slice rather than claiming every feature from the reference project is complete.

## Current capabilities

- FastAPI chat and knowledge-management APIs with Swagger documentation
- General, technical, billing or software-cost, and escalation agents
- Hybrid intent recognition using pattern rules and multilingual embeddings
- Entity extraction for order or ticket identifiers, product names, dates, amounts, and HTTP error codes
- Required-field checks and security-risk escalation policies
- Redis-backed multi-turn conversation memory
- ChromaDB-based RAG with deterministic IDs, chunking, deduplication, source tracking, and document management
- Structured HTTP error-code lookup for 401, 403, 404, and 500
- Prometheus request and latency metrics
- Offline intent evaluation and Pytest coverage for core modules

## Architecture

```text
Client
  -> FastAPI API
  -> Redis conversation history
  -> Hybrid intent recognition and entity extraction
  -> Escalation policy and agent routing
  -> Knowledge retrieval and structured tools
  -> Specialized agent and LLM
  -> Response, memory write-back, and Prometheus metrics
```

## Technology stack

- Python 3.12
- FastAPI and Pydantic
- Anthropic-compatible LLM API
- SentenceTransformers
- Redis
- ChromaDB
- Prometheus
- Docker Compose
- Pytest

## Project structure

```text
agents/       Agent interfaces, specialized agents, and orchestration
api/          FastAPI application and HTTP schemas
core/         Configuration, intent recognition, embeddings, entities, and policies
evaluation/   Offline intent-evaluation scripts and datasets
mcp/          Knowledge-base and tool-management layer
memory/       Redis conversation memory
monitoring/   Prometheus metrics and scrape configuration
tests/        Automated test suite
tools/        Deterministic structured tools
```

## Quick start

### 1. Create a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, this project uses `chromadb-client` so the local Python environment does not need to compile `chroma-hnswlib`. The ChromaDB server runs in Docker.

### 2. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and provide a valid API key. Use the same Redis password in `REDIS_PASSWORD` and `REDIS_URL`.

Never commit `.env`; it is ignored by Git.

### 3. Start infrastructure

Start Docker Desktop, then run:

```powershell
docker compose up -d
docker compose ps
```

Default development ports:

- Redis: `localhost:6380`
- ChromaDB: `localhost:8002`
- Prometheus: `http://localhost:9091`

### 4. Start the API

```powershell
python -m uvicorn api.main:app --reload --port 8003
```

Open:

- Swagger UI: `http://127.0.0.1:8003/docs`
- Health check: `http://127.0.0.1:8003/health`
- Prometheus metrics: `http://127.0.0.1:8003/metrics`

## Example chat request

```powershell
curl.exe -X POST "http://127.0.0.1:8003/chat" `
  -H "Content-Type: application/json" `
  -d '{"message":"应用登录时提示 401 错误","user_id":"demo","conv_id":"demo-session"}'
```

The response includes the selected intent and agent, confidence information, extracted entities, knowledge sources, escalation metadata, request ID, and latency.

## Knowledge-base API

The Swagger UI exposes endpoints to:

- add documents in JSON form
- upload `.txt` or `.md` files
- run semantic search
- inspect document and chunk statistics
- list logical source documents
- delete a source document and all of its chunks

Documents are split into overlapping chunks, embedded with a multilingual model, and stored in ChromaDB. Stable content-based IDs make repeat imports idempotent.

## Tests and evaluation

Run the complete automated test suite:

```powershell
python -m pytest .\tests -v
```

Run intent evaluations:

```powershell
python -m evaluation.run_intent_eval
python -m evaluation.run_hybrid_intent_eval
```

The evaluation dataset in this repository is a development dataset. Its results should not be presented as production accuracy without a larger independently reviewed test set.

## Security notes

- Secrets belong in `.env`, never in source control.
- The assistant must not request passwords, verification codes, full payment-card numbers, or complete access tokens.
- High-risk issues such as account compromise or unauthorized charges are routed to the escalation agent.
- The escalation agent creates a handoff summary; it does not claim that a real ticket was created unless an external ticketing tool confirms it.
- Change the example Redis password before using the project outside a local development environment.

## Roadmap

- LLM plus embedding plus pattern three-way intent voting
- More granular internal-IT intents and urgency levels
- Primary and supporting agent parallel collaboration
- Query rewriting, parallel retrieval, and reranking
- More structured diagnostic and ticketing tools
- Agent and tool health feedback for dynamic routing penalties
- LLM-as-Judge response-quality evaluation

