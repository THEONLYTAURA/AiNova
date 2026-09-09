# R0 Launch Checklist

## Before beta
- Run schema.sql in Supabase.
- Set production secrets on the backend only.
- Set DEMO_MODE=false.
- Set the exact production frontend origin.
- Run `pytest -q`.
- Manually test 20 prompts across weak/average/strong examples.
- Check evaluator outputs for score inflation.
- Add privacy notice and contact mechanism.

## First cohort
Target 50–100 South African students/graduates/young professionals.

Ask every beta user:
1. Did the score make sense?
2. Did you learn something new?
3. Did your second attempt improve?
4. Would you use this again tomorrow?
5. Would you pay for unlimited coaching?

## Decision rules
- If improvement is low: fix evaluator/teaching, not acquisition.
- If improvement is high but retention is low: fix challenge/progression loop.
- If retention is strong but willingness to pay is weak: investigate value proposition and target segment.
- If users pay: start R1 account and premium experiments.
