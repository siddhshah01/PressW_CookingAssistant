# Cooking Assistant

LLM-powered cooking assistant that classifies queries, searches the web when needed, generates recipes, and checks if you have the right cookware.

## Project Structure

- **backend/** – FastAPI + LangGraph backend  
  - `main.py` – API endpoints  
  - `graph.py` – LangGraph workflow  
  - `llm.py` – LLM setup  
  - `tools.py` – Web search tool  
  - `requirements.txt` – Python dependencies  

- **frontend/** – Next.js + TypeScript frontend  
  - `app/` – Next.js pages  
  - `package.json` – Node dependencies  

- `README.md` – This documentation

## What it does

- Classifies whether your question is cooking-related (rejects non-cooking questions)
- LLM decides if it needs to search the web for recipe info
- Generates recipes with step-by-step instructions
- Checks if you have the cookware needed (validates against a hardcoded list)
- Simple Next.js UI for interacting with it

## Local Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Hugging Face API token ([get one here](https://huggingface.co/settings/tokens))

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):
```bash
cp ../.env.example .env
```

5. Add your Hugging Face token to `.env`:
```
HF_TOKEN=your_actual_token_here
```

6. Run the backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Usage Examples

### Using the UI

1. Open `http://localhost:3000` in your browser
2. Type a cooking question (e.g., "How do I make pancakes?")
3. Click "Ask" and wait for the response (20-30 seconds)
4. View the recipe and cookware requirements

### Using curl

```bash
# Ask for a recipe
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I make scrambled eggs?"}'

# Non-cooking query (will be rejected)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the capital of France?"}'

# Recipe requiring unavailable cookware
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "How to make bread in a bread machine?"}'
```

### Example Response

```json
{
  "user_input": "How do I make scrambled eggs?",
  "classification": "cooking",
  "web_search_result": "...",
  "recipe": "Scrambled Eggs Recipe...\n{\"cookware_needed\": [\"Frying Pan\", \"Spatula\", \"Whisk\"]}",
  "cookware_needed": ["Frying Pan", "Spatula", "Whisk"],
  "cookware_missing": [],
  "final_answer": "Scrambled Eggs Recipe...",
  "debug": ["LLM classified as: cooking", "Web search performed", "Generated recipe", "All cookware available", "Finalized response"]
}
```

## How It Works (LangGraph Flow)

The application uses a state-based graph workflow:

1. **Classify Node**: Determines if query is cooking-related
2. **Search Node**: LLM decides whether to search web for recipe info
3. **Generate Node**: Creates detailed recipe using LLM (with search results if available)
4. **Check Node**: Validates cookware against available items
5. **Finalize Node**: Compiles final response

**Available Cookware**: Spatula, Frying Pan, Little Pot, Stovetop, Whisk, Knife, Ladle, Spoon

## Design Choices

**LangGraph**: Seemed like the right fit for managing state across multiple steps (classify → search → generate → check → finalize). Makes conditional routing pretty clean.

**DuckDuckGo**: Didn't want to deal with API keys for web search. DuckDuckGo just works through LangChain, good enough for recipes.

**Hugging Face (Mistral-7B)**: Free API, works with LangChain. Responses are slower (20-30 sec) but saves me from needing OpenAI credits.

**Tool usage**: The LLM decides whether to search or not - it's not hard-coded. Checks the query and makes a yes/no decision.

## AWS Deployment Plan

**Compute**: ECS Fargate (don't want to manage servers). Could use Lambda but cold starts would suck for UX.

**Basic setup**:
- ALB in front
- Frontend + Backend containers
- Secrets Manager for HF_TOKEN
- CloudWatch for logs

**Things I'd need to learn**:
- VPC networking (still confused about public/private subnet setup)
- Cost optimization (Fargate gets expensive)
- Auto-scaling config
- How to properly rotate secrets

## Security & Auth

**Current state**: No auth (it's just an assessment), CORS only allows localhost:3000.

**If this were production**:
- Add Cognito for user auth (JWT tokens)
- Rate limiting via AWS WAF
- HTTPS only
- Store HF_TOKEN in Secrets Manager
- Input validation (already have Pydantic models)
- Need to think about prompt injection attacks - right now it's pretty open

## Edge Cases & Limitations

**Stuff I didn't get to**:
- No conversation memory (each query is independent)
- Can't suggest cookware substitutions (just says it's missing)
- No unit conversions
- Response time is slow (20-30 sec because of HuggingFace API)
- JSON parsing breaks sometimes - need better validation
- DuckDuckGo results are inconsistent
- No retry logic if APIs fail
- Multi-day recipes (sourdough, fermentation, etc.)
- Recipe scaling / dietary restrictions

**Known bugs**:
- LLM sometimes doesn't return valid JSON for cookware list
- Search quality varies a lot

## What I prioritized (3 hour time limit)

**Got done**:
- Core workflow: classify → search → generate → check → finalize
- LangGraph with conditional routing
- Web search integration (LLM decides when to use it)
- Basic Next.js UI
- Cookware validation

**Skipped** (would've been nice):
- Docker (didn't want to spend 30+ min on config)
- Streaming responses
- Unit tests
- Better error handling
- Chat history in UI

## Things I Want to Build Next

I built a RAG system from scratch before (Whisper transcription → embedding clustering → retrieval → LLM verification). Want to apply that same ground-up approach here to understand what LangChain/LangGraph are actually abstracting.

**1. Custom memory layer** (no LangChain memory)
- Implement sliding window manually
- Use embeddings for conversation retrieval (like my past `full_docs` clustering approach)
- Understand token management better

**2. Voice input integration**
- Use my Whisper threading/queue architecture
- Stream: audio → transcribe → classify → recipe response
- Handle interruptions mid-recipe

**3. Rebuild LangGraph as simple FSM**
- Want to understand how state machines actually work
- Manual routing, no abstractions
- See how LangGraph does state persistence under the hood

**4. Custom recipe retrieval (manual RAG)**
- Build embedding + cosine similarity ranking myself
- Recipe-specific chunking (ingredients vs steps)
- Multi-stage retrieval like my past project

**5. Verification LLM**
- Like my commented-out verification code from before
- Judge LLM checks if recipe is feasible
- Multi-LLM orchestration practice

**6. Custom tool router**
- Replace LangChain's tool calling
- Simple registry: `{"search": web_search, ...}`
- Understand how agents decide to use tools

**7. ELT pipeline** (bonus requirement)
- Recipe queries → S3 → Glue → Redshift
- Dashboard for popular recipes/cookware usage
- Connect AI to data engineering

**Stuff I know from past projects**:
- Threading/async (audio chunking)
- Embedding + similarity ranking
- Semantic text chunking
- Producer-consumer queues

**What I need to learn** (LangChain hides this):
- How LangGraph does state persistence
- Tool calling protocols (ReAct pattern, function calling)
- Streaming (SSE/WebSockets)
- Prompt versioning

I learn best by building things myself first, then seeing what frameworks abstract and why.

---

## AI Tools Used

- **Claude Code**: Helped add web search integration, logging setup, and Tailwind CSS styling
- **Claude Code**: Helped structure this documentation (but ideas/content are mine)
- **Core logic built by me**: Classification flow, cookware validation, LangGraph state machine, all the node functions

The assignment requirement was to use LangChain/LangGraph, so I did. But I want to rebuild parts manually later to really understand what's happening under the hood.
