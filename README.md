# QueueStorm — Ticket Triage API

> **SUST CSE Carnival 2026 — QueueStorm Warmup: Mock Preliminary Task**

A production-ready ticket triage API that classifies customer complaints for a digital finance company. The service answers:

1. **What kind of problem is it?** (`case_type`)
2. **How serious is it?** (`severity`)
3. **Which department should handle it?** (`department`)
4. **What is a concise agent summary?** (`agent_summary`)

---

## Architecture Diagram

```
Client Request
      │
      ▼
┌─────────────┐
│  FastAPI    │  POST /sort-ticket
│  (routes)   │
└──────┬──────┘
       │
       ├──► Text Normalizer  (unicode NFC, lowercase, currency canonicalisation)
       │
       ├──► Entity Extractor (amounts, phone numbers, transaction IDs)
       │
       ├──► 4-Layer Classifier
       │         Layer 1: Regex rules          → rule_score   × 0.50
       │         Layer 2: Keyword hash-sets    → keyword_score × 0.30
       │         Layer 3: Semantic phrases     → semantic_score × 0.20
       │         Layer 4: Fallback → other
       │
       ├──► Confidence Engine  (clamp 0–1)
       │
       ├──► Human-review Gate
       │         severity==critical OR phishing OR confidence<0.65 OR large amount
       │
       └──► Summary Generator (entity-aware, credential-safe)
                  │
                  ▼
            JSON Response
```

---

## Classification Logic

### Case Types & Department Routing

| Case Type | Department |
|---|---|
| `wrong_transfer` | `dispute_resolution` |
| `payment_failed` | `payments_ops` |
| `refund_request` | `customer_support` |
| `phishing_or_social_engineering` | `fraud_risk` |
| `other` | `customer_support` |

### Severity Rules

| Severity | Triggers |
|---|---|
| `critical` | phishing, scam, fraud, OTP/PIN/password request |
| `high` | wrong transfer, payment failed, balance deducted, financial loss |
| `medium` | repeated complaint, merchant dispute |
| `low` | refund request, app issue, generic inquiry |

### Confidence Formula

```
confidence = (rule_score × 0.50) + (keyword_score × 0.30) + (semantic_score × 0.20)
```

Clamped to `[0.0, 1.0]`.

### Human Review Trigger

```python
human_review_required = (
    severity == "critical"
    OR case_type == "phishing_or_social_engineering"
    OR confidence < 0.65
    OR amount >= 10,000 BDT
)
```

---

## API Documentation

### `GET /health`

```json
{
  "status": "healthy",
  "service": "queue-storm",
  "version": "1.0.0"
}
```

### `POST /sort-ticket`

**Request body:**

```json
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number this morning, please help me get it back"
}
```

**Fields:**

| Field | Type | Required | Values |
|---|---|---|---|
| `ticket_id` | string | ✓ | 1–64 chars |
| `channel` | enum | ✓ | `app`, `web`, `sms`, `call`, `chat`, `email` |
| `locale` | enum | ✓ | `en`, `bn`, `mixed` |
| `message` | string | ✓ | 1–4096 chars |

**Response:**

```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports transferring 5000 BDT to an unintended recipient and seeks recovery assistance.",
  "human_review_required": true,
  "confidence": 0.94
}
```

**HTTP error codes:** `422 Unprocessable Entity` for validation failures, `500 Internal Server Error` for unexpected errors.

---

## Multi-Language Support

The classifier supports **English**, **Bangla**, and **mixed Bangla-English** messages.

| Message | Classified As |
|---|---|
| `"ভুল নাম্বারে টাকা পাঠিয়েছি"` | `wrong_transfer` |
| `"পেমেন্ট ফেল করেছে কিন্তু টাকা কেটে নিয়েছে"` | `payment_failed` |
| `"আমার টাকা ফেরত চাই"` | `refund_request` |
| `"কেউ OTP চাইছে"` | `phishing_or_social_engineering` |

---

## Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd queue-storm

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Docker Setup

```bash
# Build the image
docker build -t queue-storm .

# Run the container
docker run -p 8000:8000 queue-storm

# Or with docker-compose
docker-compose up --build
```

---

## Deployment Steps

### Render

1. Push your code to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com).
3. Connect your repository — Render auto-detects `render.yaml`.
4. Deploy. The `/health` endpoint is used for health checks.

### Railway

1. Push to GitHub.
2. Create a new project on [railway.app](https://railway.app) and link the repository.
3. Railway reads `railway.json` automatically.
4. Set `PORT` (Railway injects this automatically).

### Fly.io

```bash
fly launch        # first-time setup (reads fly.toml)
fly deploy        # subsequent deployments
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Server port (injected by hosting platforms) |

No secrets required — the classifier is fully rule/keyword-based.

---

## Sample Requests

```bash
# Health check
curl http://localhost:8000/health

# Wrong transfer (English)
curl -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","channel":"app","locale":"en","message":"I sent 5000 taka to a wrong number this morning"}'

# Phishing (Bangla)
curl -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-005","channel":"app","locale":"bn","message":"কেউ OTP চাইছে"}'

# Payment failed (Bangla)
curl -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-006","channel":"app","locale":"bn","message":"পেমেন্ট ফেল করেছে কিন্তু টাকা কেটে নিয়েছে"}'
```

---

## Sample Responses

**Wrong transfer:**
```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports transferring 5000 BDT to an unintended recipient and seeks recovery assistance.",
  "human_review_required": true,
  "confidence": 0.94
}
```

**Phishing:**
```json
{
  "ticket_id": "T-005",
  "case_type": "phishing_or_social_engineering",
  "severity": "critical",
  "department": "fraud_risk",
  "agent_summary": "Customer reports a suspicious request for account credentials and seeks verification of the incident.",
  "human_review_required": true,
  "confidence": 0.8
}
```

---

## Testing Instructions

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run all tests
PYTHONPATH=. pytest tests/ -v

# Run only unit tests
PYTHONPATH=. pytest tests/test_classifier.py tests/test_extractor.py -v

# Run only integration tests
PYTHONPATH=. pytest tests/test_api.py -v

# Run sample payload tests
PYTHONPATH=. pytest tests/test_payloads.py -v

# Run with coverage report
PYTHONPATH=. pytest tests/ --cov=app --cov-report=term-missing
```

---

## Project Structure

```
queue-storm/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # /health, /sort-ticket endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── ticket.py              # Pydantic request/response models + enums
│   ├── services/
│   │   ├── __init__.py
│   │   ├── classifier.py          # 4-layer engine + confidence scorer
│   │   ├── extractor.py           # Entity extraction (amounts, phones, txn IDs)
│   │   └── summarizer.py          # Agent summary generator
│   ├── classifiers/
│   │   ├── __init__.py
│   │   ├── rules.py               # Layer 1: compiled regex rules
│   │   ├── keywords.py            # Layer 2: hash-set keyword lookup
│   │   └── semantic.py            # Layer 3: semantic phrase matching
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Structured JSON logging
│       └── normalizer.py          # Text normalisation (unicode, lowercase)
├── tests/
│   ├── __init__.py
│   ├── test_api.py                # Integration tests (HTTP endpoints)
│   ├── test_classifier.py         # Unit tests (classifier logic)
│   ├── test_extractor.py          # Unit tests (entity extraction)
│   └── test_payloads.py           # Challenge sample payload tests
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── render.yaml                    # Render deployment config
├── railway.json                   # Railway deployment config
├── fly.toml                       # Fly.io deployment config
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Performance

- All classifier layers run in **O(n)** time (n = message length)
- No embedding models, vector databases, or heavy NLP pipelines
- Regex patterns compiled once at import time
- Keyword lookup via Python `frozenset` — O(1) per lookup
- Target response time: **< 100ms** under normal load
