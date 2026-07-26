# 📚 RAG Paper Explainer — v3: FastAPI + Groq + AWS EC2

**Version 3 of 3** —  enabling deployment on AWS EC2 free tier.


---
| | v2 FastAPI + Ollama | v3 FastAPI + Groq + AWS |
|---|---|---|
| LLM | Ollama (local, 4GB RAM) | Groq API (free, cloud) |
| Model | Llama 3.2 (3B) | Llama 3.3 70B (much better) |
| RAM needed | 4GB+ | 1GB (t2.micro compatible) |
| Deployable to AWS | ❌ | ✅ |
| Cost | Free (local) | Free (1,000 req/day Groq) |
| Answer quality | Good | Excellent |

The key change: swapping Ollama for Groq removes the RAM constraint and makes the app deployable on AWS EC2 free tier (t2.micro, 1GB RAM).

---

## Architecture

```
User's browser
      │  HTTPS
      ▼
AWS EC2 t2.micro (free tier)
  Ubuntu 22.04, eu-central-1 (Frankfurt)
  ┌──────────────────────────────────────┐
  │  FastAPI (main.py) on port 8000      │
  │  ├── GET  /        → index.html      │
  │  ├── GET  /health  → status          │
  │  ├── POST /upload  → index PDF       │
  │  └── POST /ask     → get answer      │
  │                                      │
  │  rag_pipeline.py                     │
  │  PyMuPDF → LangChain → ChromaDB      │
  │  sentence-transformers (local embed) │
  └──────────────────────────────────────┘
              │ API call
              ▼
         Groq API (free)
         Llama 3.3 70B
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML / CSS / JS |
| PDF parsing | PyMuPDF |
| Text chunking | LangChain Text Splitters |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2, runs on server) |
| Vector database | ChromaDB (in-memory) |
| LLM | Llama 3.3 70B via Groq API (free) |
| Deployment | AWS EC2 t2.micro (free tier, 750hrs/month) |
| Region | eu-central-1 (Frankfurt) |

---

## Project Structure

```
v3-fastapi-groq-aws/
├── main.py           # FastAPI backend with Groq API integration
├── rag_pipeline.py   # RAG logic using Groq instead of Ollama
├── index.html        # Frontend with Groq API key input
├── requirements.txt  # No ollama/torch — lightweight for EC2
└── README.md
```

---

## Prerequisites

- AWS account (free: aws.amazon.com)
- Groq API key (free, no credit card: console.groq.com)
- Python 3.10+ (for local testing)

---

## Step 1: Get a Free Groq API Key

```
1. Go to console.groq.com
2. Sign up with Google (no credit card required)
3. API Keys → Create API Key
4. Copy the key — starts with gsk_...
```

Free tier: **1,000 requests/day** — sufficient for personal and demo use.

---

## Step 2: Test Locally First

```bash
cd v3-fastapi-groq-aws

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

Open **http://localhost:8000**, enter your Groq key, upload a PDF, ask a question.

---

## Step 3: Deploy to AWS EC2

### 3a. Launch EC2 Instance

```
AWS Console → EC2 → Launch Instance

Settings:
  Name:           rag-paper-explainer
  OS:             Ubuntu 22.04 LTS (free tier eligible)
  Instance type:  t2.micro (free tier — 750hrs/month free)
  Key pair:       Create new → download .pem file

Network settings → Edit:
  Add rule: Type = Custom TCP
            Port = 8000
            Source = 0.0.0.0/0

→ Click Launch Instance
```

### 3b. Connect to Your Instance

```bash
# On  PC:
chmod 400 ~/Downloads/your-key.pem

ssh -i ~/Downloads/your-key.pem ubuntu@EC2-PUBLIC-IP
```

Find your public IP in: EC2 Console → Instances → your instance → Public IPv4 address

### 3c. Set Up the Server

```bash
# On EC2 (after SSH in):
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv -y

mkdir rag-app && cd rag-app
python3 -m venv venv
source venv/bin/activate
```

### 3d. Upload  Files

```bash
Open a  terminal window:
cd path/to/v3-fastapi-groq-aws

scp -i ~/Downloads/your-key.pem \
    main.py \
    rag_pipeline.py \
    index.html \
    requirements.txt \
    ubuntu@YOUR-EC2-IP:~/rag-app/
```

### 3e. Install Dependencies and Run

```bash
# Back on EC2:
cd ~/rag-app
source venv/bin/activate
pip install -r requirements.txt

# Run in background 
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &

# Verify it's running:
curl http://localhost:8000/health
```

### 3f. Access  Live App

```
Open in browser:
http://YOUR-EC2-PUBLIC-IP:8000
```

---

## Usage

1. Open the app URL in your browser
2. Enter your free Groq API key in the sidebar
3. Upload a research paper PDF
4. Wait ~10 seconds for indexing
5. Ask questions or use the quick action buttons

---

## API Reference

### `POST /upload`

Upload and index a PDF.

**Form data:**
```
file          PDF file (multipart)
groq_api_key  Your Groq API key
```

**Response:**
```json
{
  "status": "ok",
  "message": "Loaded: Paper Title Here",
  "chunks": 142
}
```

### `POST /ask`

Ask a question about the loaded paper.

**Request body:**
```json
{
  "question": "What methods did the authors use?",
  "groq_api_key": "gsk_..."
}
```

**Response:**
```json
{
  "answer": "According to Page 4, the authors used..."
}
```

### `GET /health`

```json
{"status": "ok", "model": "llama-3.3-70b via Groq"}
```

Interactive API docs (auto-generated by FastAPI): `http://YOUR-IP:8000/docs`

---

## Managing the Server

```bash
# Check if it's running:
ps aux | grep uvicorn

# Stop the server:
pkill -f uvicorn

# Restart:
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &

# View logs:
cat nohup.out

# Stop EC2 instance (to pause billing):
# AWS Console → EC2 → Instances → Stop Instance
# Note: stopping pauses compute billing but keeps storage
```

---

## AWS Cost Management

```
Free tier covers:
  750 hours/month t2.micro = run 24/7 for 12 months free
  30GB EBS storage

After 12 months free tier expires:
  t2.micro costs ~$8.47/month in eu-central-1

To avoid surprise charges:
  → Set a billing alarm in AWS Billing Dashboard
  → Stop the instance when not in use
  → The app doesn't need to run 24/7 for a portfolio demo
```

---


## Related Projects

- **[Autonomous Literature Review Agent](../../lit-review-agent)** — give it a topic, it autonomously searches PubMed and ArXiv and writes a structured review
- **[PRS Analysis Pipeline](../../prs-agent)** — end-to-end polygenic risk score computation (Python, Nextflow, Docker)
- **[Customer Churn Prediction](../../churn-xgboost)** — XGBoost classifier with AUC 0.84, deployed as a REST API
