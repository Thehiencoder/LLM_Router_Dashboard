# LLM Router Dashboard

A state-of-the-art interactive dashboard for side-by-side response, latency, token count, and cost benchmarking across **GPT (OpenAI)**, **Claude (Anthropic)**, and **Gemini (Google)**.

![Architecture](https://img.shields.io/badge/Architecture-Decoupled_Adapter_Pattern-blue)
![Python](https://img.shields.io/badge/Python-3.13+-brightgreen)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)

---

## Features

- **Side-by-Side Comparison:** Compare responses from next-gen models (GPT-4.5 / o3-mini, Claude 3.7 Sonnet / Claude 4, Gemini 3.0 / 3.8 Flash).
- **Comprehensive Metrics:**
  - **Latency (ms):** Measured precisely around inference calls using `time.perf_counter()`.
  - **Token Counts:** Detailed breakdown of input, output, reasoning/thinking, and total tokens.
  - **Estimated & Actual Cost:** Transparent cost accounting including **Gemini Free Tier ($0.00 actual)** vs commercial rates and paid credits for Claude/GPT.
- **Fault-Tolerant Async Concurrency:** Non-blocking query execution powered by Python 3.13 structured concurrency. If one provider fails (e.g., rate limit or missing key), other providers render seamlessly.
- **Provider Adapter Architecture:** Standardized `BaseLLMProvider` interface decouples the frontend and API from individual SDK idiosyncrasies.
- **Built-in Mock Mode:** Immediate testing without requiring active paid API keys.

---

## Tech Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Backend:** FastAPI, Pydantic v2, Python 3.13+ `asyncio`.
- **SDKs:** `openai`, `anthropic`, `google-genai`.

---

## Quick Start

### 1. Environment Configuration

Copy the sample environment file and set your keys (or leave empty to test in mock mode):

```bash
cp .env.example .env
```

### 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://127.0.0.1:8000` (API docs at `http://127.0.0.1:8000/docs`).

### 3. Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend dashboard will open at `http://localhost:5173`.
