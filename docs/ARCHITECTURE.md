# R0 Architecture Decisions

## Static frontend
Chosen because R0 needs no build pipeline and can be hosted cheaply. React can be introduced when component complexity or team velocity clearly justifies it.

## FastAPI monolith
Chosen because the product has a handful of synchronous routes. Microservices, queues and websockets add operational overhead before there is traffic to justify them.

## Supabase/Postgres
Chosen for managed Postgres plus simple operations. No custom database infrastructure.

## Single evaluation service
All AI scoring goes through one evaluator so the rubric, output schema, model and evaluator version stay consistent.

## Application-owned score
The LLM produces dimension evidence and dimension scores. Python calculates the weighted composite. This reduces arbitrary headline-score drift.

## Demo mode
A deterministic local mode makes onboarding, frontend development and demos possible without paid services. It must remain disabled in production.

## Future bottlenecks
1. Evaluation consistency — solve with benchmark calibration and versioning.
2. API cost — solve with quotas, shorter prompts/outputs, caching and model routing.
3. Synchronous latency — introduce background jobs only when real traffic demonstrates the need.
4. Anonymous-session abuse — add stronger bot controls and authenticated quotas in R1.
