# FitPlanAI

Final project for the Building AI course

## Summary
**Building AI course project** — A smart weekly workout planner that builds a 7-day plan based on your **available equipment**, **time per day**, and **goals** (strength/cardio/mobility), while balancing muscle groups and avoiding back-to-back repeats.

## Background
Planning workouts is hard: equipment differs, time is limited, and repeating the same muscles hurts adherence. FitPlanAI creates a simple, realistic 7-day plan from what you already have at home, your time limit, and your goals — so you can just press “go”.

## Data and AI techniques
- **Data**
  - `data/exercises.csv` — sample exercises with tags, equipment, time, and muscles.
  - User configuration (available equipment, goals, time per day) inside the script.
- **Features**
  - Equipment feasibility check (must match your gear).
  - Time constraint per day.
  - Goal matching (strength/cardio/mobility).
  - Muscle balance (penalize back-to-back same primary muscle).
- **Methods (prototype)**
  - Content-based scoring: goal match + time fit − repeat-muscle penalty.
  - Greedy selection to fill **7 days** without repeating the exact exercise.
  - (Roadmap) Personalization via ratings, progressive overload, injury flags.

## How is it used?
1. Edit configuration at the top of `src/fitplan.py` (goals, time limit, equipment).
2. Run the planner to get a 7-day plan with titles, time, equipment, tags, and muscles.

### Quick start
```bash
# optional venv
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt   # no external deps, kept for consistency
python3 src/fitplan.py
