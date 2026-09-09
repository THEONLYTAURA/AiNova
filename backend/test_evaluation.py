import json, os
os.environ["DEMO_MODE"]="true"
from scoring import *
from evaluation import evaluate_prompt

def test_weighted_score():
    scores={"context":80,"task_clarity":80,"specificity":60,"constraints":60,"output_format":100,"examples":100,"evaluation":40}
    assert composite_score(scores)==74

def test_levels_cover_all_scores():
    assert {level_for_score(i) for i in range(101)} == {x[2] for x in LEVEL_BANDS}
    assert level_for_score(0)=="AI Novice"; assert level_for_score(100)=="AI Expert"

def test_improvement_rate():
    assert prompt_improvement_rate(42,82)==69.0
    assert prompt_improvement_rate(100,100)==0.0

def test_demo_evaluator_returns_deterministic_composite():
    r=evaluate_prompt("Write a study plan for a university student. Use a table and verify the schedule.")
    assert 0 <= r["score"] <= 100
    assert set(r["dimensions"]) == set(RUBRIC_WEIGHTS)

def test_missing_dimension_rejected():
    try: composite_score({"context":10})
    except ValueError: pass
    else: raise AssertionError("expected missing dimension failure")
