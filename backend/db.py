from __future__ import annotations
import datetime as dt
import os
import uuid
from typing import Any

MEM_SESSIONS: dict[str, dict[str, Any]] = {}
MEM_EVENTS: dict[str, list[dict[str, Any]]] = {}
MEM_COACH: dict[str, list[dict[str, Any]]] = {}
MEM_CHALLENGES = [
    {"id":"demo-1","title":"Lecture notes to study guide","scenario":"Turn messy lecture notes into a structured study guide with headings and a short quiz.","category":"study","difficulty":"easy"},
    {"id":"demo-2","title":"CV bullet points that land","scenario":"Rewrite three flat CV bullet points into achievement-focused bullets without inventing facts.","category":"career","difficulty":"medium"},
    {"id":"demo-3","title":"Client deadline email","scenario":"Draft a clear, professional email explaining a one-week delay without making excuses.","category":"work","difficulty":"medium"},
]

def _demo() -> bool:
    return os.getenv("DEMO_MODE", "false").lower() == "true"

def _client():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

def get_or_create_session(session_id: str | None) -> str:
    if _demo():
        if session_id and session_id in MEM_SESSIONS:
            MEM_SESSIONS[session_id]["last_seen_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            return session_id
        sid = str(uuid.uuid4()); MEM_SESSIONS[sid] = {"id": sid}; MEM_EVENTS.setdefault(sid, []); return sid
    client = _client()
    if session_id:
        found = client.table("sessions").select("id").eq("id", session_id).execute()
        if found.data:
            client.table("sessions").update({"last_seen_at": dt.datetime.now(dt.timezone.utc).isoformat()}).eq("id", session_id).execute()
            return session_id
    created = client.table("sessions").insert({}).execute()
    return created.data[0]["id"]

def log_progress_event(session_id: str, event_type: str, score: int):
    row = {"event_type": event_type, "score": score, "created_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    if _demo(): MEM_EVENTS.setdefault(session_id, []).append(row); return
    _client().table("progress_events").insert({"session_id":session_id,"event_type":event_type,"score":score}).execute()

def get_progress_events(session_id: str):
    if _demo(): return MEM_EVENTS.get(session_id, [])
    return _client().table("progress_events").select("event_type, score, created_at").eq("session_id",session_id).order("created_at").execute().data

def get_todays_challenge():
    if _demo(): return MEM_CHALLENGES[0]
    today = dt.date.today().isoformat()
    result = _client().table("challenges").select("id,title,scenario,category,difficulty").eq("active_date",today).limit(1).execute()
    if result.data: return result.data[0]
    fallback = _client().table("challenges").select("id,title,scenario,category,difficulty").is_("active_date","null").limit(1).execute()
    return fallback.data[0] if fallback.data else None

def get_challenge(challenge_id: str):
    if _demo(): return next((x for x in MEM_CHALLENGES if x["id"] == challenge_id), None)
    r = _client().table("challenges").select("id,title,scenario,category,difficulty").eq("id",challenge_id).limit(1).execute()
    return r.data[0] if r.data else None

def save_coach(session_id: str, prompt: str, result: dict):
    if _demo(): MEM_COACH.setdefault(session_id, []).append({"prompt":prompt, **result}); return
    _client().table("coach_submissions").insert({"session_id":session_id,"submitted_prompt":prompt,"overall_score":result["score"],"dimension_scores":result["dimensions"],"missing_elements":result["weaknesses"],"improved_prompt":result["improved_prompt"],"explanation":result["explanation"],"lesson_dimension":result["lesson_dimension"],"evaluator_version":result["evaluator_version"],"model":result["model"]}).execute()

def save_challenge(session_id: str, challenge_id: str, prompt: str, result: dict):
    if _demo(): return
    _client().table("challenge_submissions").insert({"session_id":session_id,"challenge_id":challenge_id,"submitted_prompt":prompt,"overall_score":result["score"],"dimension_scores":result["dimensions"],"feedback":result["explanation"],"improved_prompt":result["improved_prompt"],"lesson_dimension":result["lesson_dimension"]}).execute()

def save_skill_test(session_id: str, score: int, level: str, dimensions: dict, weaknesses: list[str], answers: list[dict]):
    if _demo():
        log_progress_event(session_id,"skill_test",score); return
    client = _client()
    attempt = client.table("skill_test_attempts").insert({"session_id":session_id,"completed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"overall_score":score,"level":level,"dimension_scores":dimensions,"weaknesses":weaknesses}).execute()
    attempt_id = attempt.data[0]["id"]
    rows=[{"attempt_id":attempt_id,**a} for a in answers]
    client.table("skill_test_answers").insert(rows).execute()
    log_progress_event(session_id,"skill_test",score)
