create extension if not exists pgcrypto;

create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  email text,
  created_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now()
);

create table if not exists skill_test_attempts (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id) on delete cascade,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  overall_score integer check (overall_score between 0 and 100),
  level text,
  dimension_scores jsonb,
  weaknesses jsonb
);

create table if not exists skill_test_answers (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid not null references skill_test_attempts(id) on delete cascade,
  question_id text not null,
  question_type text not null check (question_type in ('prompt_write','scenario_mcq')),
  answer_text text not null,
  score integer check (score between 0 and 100),
  dimension text,
  created_at timestamptz not null default now()
);

create table if not exists coach_submissions (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id) on delete cascade,
  submitted_prompt text not null,
  overall_score integer not null check (overall_score between 0 and 100),
  dimension_scores jsonb not null,
  missing_elements jsonb,
  improved_prompt text,
  explanation text,
  lesson_dimension text,
  evaluator_version text,
  model text,
  created_at timestamptz not null default now()
);

create table if not exists challenges (
  id uuid primary key default gen_random_uuid(),
  title text not null unique,
  scenario text not null,
  category text,
  difficulty text check (difficulty in ('easy','medium','hard')),
  active_date date,
  created_at timestamptz not null default now()
);

create table if not exists challenge_submissions (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id) on delete cascade,
  challenge_id uuid not null references challenges(id),
  submitted_prompt text not null,
  overall_score integer not null check (overall_score between 0 and 100),
  dimension_scores jsonb not null,
  feedback text,
  improved_prompt text,
  lesson_dimension text,
  created_at timestamptz not null default now()
);

create table if not exists progress_events (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id) on delete cascade,
  event_type text not null check (event_type in ('skill_test','coach','challenge')),
  score integer not null check (score between 0 and 100),
  created_at timestamptz not null default now()
);

create table if not exists lessons (
  id text primary key,
  title text not null,
  content_md text not null,
  sort_order integer not null default 0
);

create index if not exists idx_progress_session_created on progress_events(session_id,created_at);
create index if not exists idx_coach_session_created on coach_submissions(session_id,created_at);
create index if not exists idx_challenge_session_created on challenge_submissions(session_id,created_at);
create index if not exists idx_skill_attempt_session on skill_test_attempts(session_id,started_at);

insert into lessons(id,title,content_md,sort_order) values
('context','Give the AI the situation','Context tells the AI who the output is for, why it matters and what situation it is operating in.',1),
('task_clarity','Name the actual task','Replace vague requests with a concrete action and desired outcome.',2),
('specificity','Concrete beats general','Use useful details, quantities, names and scope to reduce guesswork.',3),
('constraints','Set boundaries','Length, tone, exclusions, source requirements and limits make outputs more reliable.',4),
('output_format','Specify the shape','Tell the model whether you need a table, bullets, JSON, sections or another structure.',5),
('examples','Show the target','A relevant example can communicate style and quality faster than abstract instructions.',6),
('evaluation','Build in verification','Ask for source checking, assumptions, uncertainty or success criteria when accuracy matters.',7)
on conflict(id) do nothing;

insert into challenges(title,scenario,category,difficulty,active_date) values
('Lecture notes to study guide','Turn messy lecture notes into a structured study guide with headings and a short quiz.','study','easy',current_date),
('CV bullet points that land','Rewrite three flat CV bullet points into achievement-focused bullets without inventing facts.','career','medium',null),
('Client deadline email','Draft a clear professional email explaining a one-week delay without making excuses.','work','medium',null)
on conflict(title) do nothing;
