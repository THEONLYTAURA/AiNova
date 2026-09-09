# PromptForge R0

A production-minded, low-cost MVP for measuring and improving practical AI skills.

## R0 product loop

**Measure → Teach → Practice → Re-attempt → Measure again**

R0 includes:
- Anonymous sessions
- 10-question AI Skill Test
- Prompt Coach
- Daily Challenges
- Progress timeline
- Evidence-based 7-dimension scoring
- LLM structured output
- Rate limiting and input limits
- Analytics event hooks
- Golden evaluation benchmark scaffold
- Responsive vanilla HTML/CSS/JS frontend

## Stack

- Frontend: static HTML/CSS/JavaScript
- Backend: Python + FastAPI
- Database: Supabase/PostgreSQL
- AI: OpenAI API
- Hosting: any static host + Render/Railway/Fly/etc. for API

## Local setup

1. Create a Supabase project and run `schema.sql`.
2. `cd backend && python -m venv .venv`
3. Activate the environment and install `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set keys.
5. Run `uvicorn main:app --reload --port 8000`.
6. Serve `frontend/` with any static server, e.g. `python -m http.server 5500` from the frontend folder.
7. Open the frontend and set API base to `http://localhost:8000` if needed.

## Demo mode

Set `DEMO_MODE=true` to run the complete frontend/backend flow without Supabase or OpenAI. This is for development and demos only. It uses deterministic local evaluation fixtures and an in-memory store.

## Production rules

- Never expose OpenAI or Supabase service-role credentials to the browser.
- Use HTTPS in production.
- Keep RLS enabled if clients ever access Supabase directly.
- Review privacy/POPIA obligations before collecting identifiable information.
- Treat user prompts as untrusted data.
- Version the evaluator rubric and model.

## Tests

From `backend/`:

`python -m pytest -q`

The tests cover scoring math, level bands, schema validation, input limits and evaluator failure handling.
