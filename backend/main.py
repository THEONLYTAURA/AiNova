from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import db
from evaluation import evaluate_prompt
from question_bank import QUESTIONS
from scoring import composite_score, level_for_score, prompt_improvement_rate
from schemas import *

MAX_PROMPT = int(os.getenv("MAX_PROMPT_CHARS", "4000"))
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="PromptForge API", version="0.2.0", description="PromptForge R0 AI-skills platform")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
origins = [x.strip() for x in os.getenv("FRONTEND_ORIGIN", "http://localhost:5500").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["*"])

def _clean_prompt(prompt: str) -> str:
    value = prompt.strip()
    if len(value) > MAX_PROMPT: raise HTTPException(413, f"Prompt exceeds {MAX_PROMPT} characters.")
    if len(value) < 3: raise HTTPException(400, "Write at least a short sentence so we can evaluate it.")
    return value

@app.get("/api/health")
def health():
    return {"status":"ok","demo_mode":os.getenv("DEMO_MODE","false").lower()=="true","version":app.version}

@app.post("/api/session")
def create_session(session_id: str | None = None):
    return {"session_id": db.get_or_create_session(session_id)}

@app.get("/api/skill-test/questions")
def skill_test_questions():
    return [{k:v for k,v in q.items() if k not in {"answer"}} for q in QUESTIONS]

@app.post("/api/skill-test/submit")
@limiter.limit("10/hour")
def skill_test_submit(request: Request, payload: SkillTestSubmitRequest):
    session_id = db.get_or_create_session(payload.session_id)
    answer_map = {a.question_id:a.answer.strip() for a in payload.answers}
    if set(answer_map) != {q["id"] for q in QUESTIONS}: raise HTTPException(400,"Exactly the current 10 questions must be answered.")
    dimension_scores={d:0 for d in ["context","task_clarity","specificity","constraints","output_format","examples","evaluation","workflow_thinking","critical_evaluation","iteration"]}
    scored=[]
    for q in QUESTIONS:
        answer=answer_map[q["id"]]
        if q["type"] == "scenario_mcq":
            score=100 if answer.lower() == q["answer"] else 0
        else:
            # Each writing item is evaluated against the shared seven-dimension engine.
            result=evaluate_prompt(answer, q["scenario"])
            score=result["dimensions"].get(q["competency"], result["score"])
        dimension_scores[q["competency"]]=score
        scored.append({"question_id":q["id"],"question_type":q["type"],"answer_text":answer,"score":score,"dimension":q["competency"]})
    overall=round(sum(dimension_scores.values())/len(dimension_scores))
    # Map the ten competencies into the seven core reporting dimensions.
    core={k:0 for k in ["context","task_clarity","specificity","constraints","output_format","examples","evaluation"]}
    mapping={"context":"context","task_clarity":"task_clarity","specificity":"specificity","constraints":"constraints","output_format":"output_format","examples":"examples","evaluation":"evaluation","workflow_thinking":"evaluation","critical_evaluation":"evaluation","iteration":"evaluation"}
    buckets={k:[] for k in core}
    for k,v in dimension_scores.items(): buckets[mapping[k]].append(v)
    core={k:round(sum(v)/len(v)) for k,v in buckets.items()}
    overall=composite_score(core)
    weaknesses=sorted(core,key=core.get)[:2]
    db.save_skill_test(session_id,overall,level_for_score(overall),core,weaknesses,scored)
    return {"session_id":session_id,"score":overall,"level":level_for_score(overall),"dimensions":core,"dimension_evidence":{},"weaknesses":weaknesses,"improved_prompt":"","explanation":"Your result combines practical prompt-writing and AI-use judgement.","lesson_dimension":weaknesses[0],"evaluator_version":"r0.2","model":"mixed"}

@app.post("/api/coach/evaluate", response_model=EvaluationResult)
@limiter.limit("20/hour")
def coach_evaluate(request: Request, payload: CoachRequest):
    prompt=_clean_prompt(payload.prompt); session_id=db.get_or_create_session(payload.session_id)
    try: result=evaluate_prompt(prompt)
    except Exception as exc: raise HTTPException(502,"The AI evaluator is temporarily unavailable. Try again in a moment.") from exc
    db.save_coach(session_id,prompt,result); db.log_progress_event(session_id,"coach",result["score"])
    return {**result,"session_id":session_id}

@app.post("/api/coach/retry", response_model=EvaluationResult)
@limiter.limit("20/hour")
def coach_retry(request: Request, payload: RetryRequest):
    prompt=_clean_prompt(payload.prompt); session_id=db.get_or_create_session(payload.session_id)
    try: result=evaluate_prompt(prompt)
    except Exception as exc: raise HTTPException(502,"The AI evaluator is temporarily unavailable. Try again in a moment.") from exc
    db.save_coach(session_id,prompt,result); db.log_progress_event(session_id,"coach",result["score"])
    result["improvement"] = result["score"] - payload.previous_score
    result["improvement_rate"] = prompt_improvement_rate(payload.previous_score,result["score"])
    return {**result,"session_id":session_id}

@app.get("/api/challenge/today", response_model=ChallengeOut)
def challenge_today():
    c=db.get_todays_challenge()
    if not c: raise HTTPException(404,"No challenge available.")
    return c

@app.post("/api/challenge/submit", response_model=EvaluationResult)
@limiter.limit("20/hour")
def challenge_submit(request: Request, payload: ChallengeSubmitRequest):
    prompt=_clean_prompt(payload.prompt); session_id=db.get_or_create_session(payload.session_id); challenge=db.get_challenge(payload.challenge_id)
    if not challenge: raise HTTPException(404,"Unknown challenge_id.")
    try: result=evaluate_prompt(prompt, challenge["scenario"])
    except Exception as exc: raise HTTPException(502,"The AI evaluator is temporarily unavailable. Try again in a moment.") from exc
    db.save_challenge(session_id,payload.challenge_id,prompt,result); db.log_progress_event(session_id,"challenge",result["score"])
    return {**result,"session_id":session_id}

@app.get("/api/progress", response_model=ProgressResponse)
def progress(session_id: str):
    events=db.get_progress_events(session_id)
    scores=[e["score"] for e in events]
    return {"events":events,"current_score":scores[-1] if scores else None,"improvement":(scores[-1]-scores[0]) if len(scores)>1 else None}
