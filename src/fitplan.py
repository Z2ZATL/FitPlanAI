from pathlib import Path
import csv
import math
from typing import List, Dict, Set, Tuple

# ====== User Configuration ======
DAYS = 7
TIME_PER_DAY = 30                            # minutes per day
GOALS: Set[str] = {"strength", "cardio"}     # any of {"strength","cardio","mobility"}
AVAILABLE_EQUIP: Set[str] = {
    "bodyweight", "dumbbell", "kettlebell", "mat", "jump rope", "bike", "band"
}
AVOID_TAGS: Set[str] = set()                 # e.g., {"hiit"} if recovering

# ====== Data paths (robust relative to this file) ======
ROOT = Path(__file__).resolve().parents[1]
EXERCISES_CSV = ROOT / "data" / "exercises.csv"

# ====== Data model ======
class Exercise:
    def __init__(self, row: Dict[str, str]):
        self.id = int(row["id"])
        self.title = row["title"].strip()
        self.tags = [t.strip() for t in row["tags"].split(";") if t.strip()]
        self.time = int(row["time_mins"])
        self.equipment = [e.strip() for e in row["equipment"].split(";") if e.strip()]
        self.muscles = [m.strip() for m in row["muscles"].split(";") if m.strip()]

    @property
    def primary_muscle(self) -> str:
        return self.muscles[0] if self.muscles else "full-body"

def load_exercises(path: Path) -> List[Exercise]:
    items: List[Exercise] = []
    with path.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            items.append(Exercise(row))
    return items

def equipment_feasible(ex: Exercise) -> bool:
    # "none" implies no equipment required
    if len(ex.equipment) == 0 or ex.equipment == ["none"]:
        return True
    # all required equipment must be available
    return all(req in AVAILABLE_EQUIP for req in ex.equipment)

def candidate_filter(ex: Exercise) -> bool:
    if ex.time > TIME_PER_DAY:
        return False
    if any(tag in AVOID_TAGS for tag in ex.tags):
        return False
    if not equipment_feasible(ex):
        return False
    return True

def score(ex: Exercise, prev_primary: str | None) -> float:
    # goal match
    goal_hit = len(set(ex.tags) & GOALS) / max(1, len(GOALS))  # 0..1
    # time fit (closer to TIME_PER_DAY is a bit better)
    time_fit = max(0.0, 1.0 - abs(ex.time - TIME_PER_DAY) / max(1, TIME_PER_DAY))
    # penalty for repeating same primary muscle as previous day
    repeat_pen = 0.3 if (prev_primary and ex.primary_muscle == prev_primary) else 0.0
    return 0.6 * goal_hit + 0.4 * time_fit - repeat_pen

def plan_week(exercises: List[Exercise]) -> List[Exercise]:
    # Pre-filter feasible exercises
    feas = [ex for ex in exercises if candidate_filter(ex)]
    chosen: List[Exercise] = []
    used_titles: Set[str] = set()
    prev_primary: str | None = None

    for day in range(DAYS):
        # rank candidates for this day
        ranked = sorted(
            (ex for ex in feas if ex.title not in used_titles),
            key=lambda ex: score(ex, prev_primary),
            reverse=True
        )
        if not ranked:
            # fallback: pick any equipment-feasible regardless of time (should be rare)
            backup = [ex for ex in exercises if equipment_feasible(ex) and ex.title not in used_titles]
            if not backup:
                break
            pick = sorted(backup, key=lambda ex: score(ex, prev_primary), reverse=True)[0]
        else:
            pick = ranked[0]
        chosen.append(pick)
        used_titles.add(pick.title)
        prev_primary = pick.primary_muscle
    return chosen

def main():
    exs = load_exercises(EXERCISES_CSV)
    plan = plan_week(exs)

    goals_str = ", ".join(sorted(GOALS)) if GOALS else "none"
    print("=== FitPlanAI (prototype) ===")
    print(f"Days: {DAYS} | Time/day: {TIME_PER_DAY} min | Goals: {goals_str}")
    print(f"Chosen {len(plan)} sessions\n")

    for i, ex in enumerate(plan, start=1):
        equip = ", ".join(ex.equipment) if ex.equipment else "none"
        tags = "; ".join(ex.tags)
        muscles = "; ".join(ex.muscles)
        print(f"Day {i}: {ex.title}  ({ex.time} min)  equip: {equip}")
        print(f"  tags: {tags} | muscles: {muscles}")

    if len(plan) < DAYS:
        print("\nNote: Not enough feasible sessions under current constraints.")

if __name__ == "__main__":
    main()
