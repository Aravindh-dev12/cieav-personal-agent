# CIEAV: Sovereign Safety Floor & Gateway Architecture

> *"Committed is not the same as succeeded."*

The `commit_layer` package provides the sovereign safety control plane that mediates actions between autonomous personal AI agents and consequential side effects.

---

## Architecture & Transaction Pipeline

```text
Agent / MCP Client / Caller
            │
            ▼
┌──────────────────────────────────────────────┐
│             CIEAV SAFETY GATEWAY             │
│                                              │
│  1. Intercept & Normalize Tool Call          │
│  2. Sanitize & Redact Secrets (privacy.py)   │
│  3. Deterministic Safety Floor (policy.py)   │
│  4. Risk Evaluation:                         │
│     - Local Decision Model (decision_model)  │
│     - AWS Bedrock Converse (optional)        │
│     - Crustdata Payee Verification (optional)│
│     * Consequence Algebra: Risk only climbs  │
│  5. Cognitive Friction Engine (friction.py)  │
│  6. Single-Use Execution Token (tokens.py)   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│           SANDBOX & TARGET RUNTIMES          │
│                                              │
│  7. Capture Pre-Execution State Snapshot     │
│  8. Execute Tool Action                      │
│  9. Capture Post-Execution State Snapshot    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│          OUTCOME & RECEIPT VERIFICATION      │
│                                              │
│ 10. Observer Evaluates State Delta           │
│     - OBSERVED_SUCCESS                       │
│     - OBSERVED_FAILURE                       │
│     - UNKNOWN (Verification inconclusive)    │
│ 11. Ed25519 Signed Receipt Append-Only Store │
│ 12. SHA-256 Hash Chain Linking (receipts.py) │
│ 13. Two-Phase Undo (Only if observed success │
│     and valid inverse function registered)   │
└──────────────────────────────────────────────┘
```

---

## Core Invariants

1. **Safety Floor is Immutable**: The AI classifier can **only raise risk**, never lower it. Deterministic policy rules dictate the minimum floor.
2. **HIGH and CRITICAL Never Auto-Execute**: Even if a human operator approves several actions in quick succession, high-consequence operations always require typed confirmation.
3. **Committed ≠ Succeeded**: Actions transition to `COMMITTED` upon entering execution, but their consequence is independently observed as `OBSERVED_SUCCESS`, `OBSERVED_FAILURE`, or `UNKNOWN`.
4. **Strict Undo Invariant**: Undo is permitted **only if** outcome is `OBSERVED_SUCCESS` **and** the tool registers a reversible inverse function. Ambiguous outcomes (`UNKNOWN`) forbid Undo.
5. **Privacy First**: Secrets, card numbers, passwords, and tokens are scrubbed *before* reaching loggers, telemetry, or decision models.
6. **Cryptographic Tamper-Evidence**: Every receipt is signed with local Ed25519 keys and linked via SHA-256 hashes (`GET /api/receipts/verify`).
7. **Offline-Native Default**: Operates out-of-the-box with zero external API keys via the embedded Bayesian decision engine (`cieav-decider-mini`).

---

## Integrated Modules

- **`decision_model.py`**: Embedded `/v1/decisions` and `/v1/systemone` engine. Answers typed decision questions (predicates, choice distributions, scores) in <3ms.
- **`poppy.py`**: Autonomous Agent Gateway Protocol. Implements discovery at `/.well-known/poppy.json`, session issuance, and governed multi-turn dialogues.
- **`webzero.py`**: Governed Action Surfaces engine. Enforces idempotency keys, Trajectory Evidence hashing, and surface readiness evaluation.
- **`headroom/`**: Context optimization middleware. Compresses JSON, code, and logs into a local content-addressable CCR vault, saving up to 95.8% of tokens.
- **`memorable.py`**: Procedural graph memory. Caches verified `(precondition -> action -> postcondition -> outcome)` graphs in SQLite to bypass repetitive LLM turns safely.
- **`connectors.py`**: Open connector & sovereign workspace module for managing external service integrations through the commit gateway.
- **`crustdata.py`**: Payee and vendor verification client for financial transactions.
- **`telemetry.py`**: Structured tracing client for Neatlogs.

---

## Environment Setup

Configure `.env` in the repository root:

```env
# ---------------------------------------------------------------------------
# 1. Neatlogs (Tracing & Observability)
# ---------------------------------------------------------------------------
NEATLOGS_API_KEY=your-neatlogs-project-key

# ---------------------------------------------------------------------------
# 2. AWS Bedrock (Claude Haiku 4.5 via Bedrock Converse API)
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# ---------------------------------------------------------------------------
# 3. Crustdata (Payee / Counterparty Verification)
# ---------------------------------------------------------------------------
CRUSTDATA_API_KEY=your-crustdata-key

# ---------------------------------------------------------------------------
# 4. Local Decision Model Configuration
# ---------------------------------------------------------------------------
CIEAV_DECISION_MODEL_ENABLED=1
CIEAV_DECISION_MODEL=cieav-decider-mini
```

*Note: No third-party LLM keys (OpenAI, Anthropic, Gemini) are required for core operations.*

---

## Running and Verifying

### Start Gateway
```bash
python -m uvicorn commit_layer.app:app --host 127.0.0.1 --port 8000 --reload
```

### Run Unit Tests
```bash
python -m pytest commit_layer/tests/ -v
```

### Run Live End-to-End Test (14 Stages)
```bash
python commit_layer/live_e2e_test.py
```

### Run Adversarial Red Team Suite
```bash
python -m commit_layer.redteam
```
