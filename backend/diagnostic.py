import math
import os
import json
from typing import List, Dict, Any, Optional

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


def classify_topic_gap(correct: int, total: int, exam_frequency: int) -> Dict[str, Any]:
    """
    Classifies a topic based on student quiz accuracy:
    - Weak: < 50%
    - Medium: 50% - 79%
    - Strong: >= 80%
    Priority score combines knowledge deficit (1 - accuracy) with exam importance.
    """
    accuracy = (correct / total) if total > 0 else 0.0

    if total == 0:
        # Unattempted: if it has high exam frequency, it's urgent to diagnose
        status = "Weak" if exam_frequency >= 3 else "Medium"
        color = "red" if status == "Weak" else "yellow"
        accuracy = 0.0
    elif accuracy < 0.50:
        status = "Weak"
        color = "red"
    elif accuracy < 0.80:
        status = "Medium"
        color = "yellow"
    else:
        status = "Strong"
        color = "green"

    # Higher score = higher urgency in the revision plan
    priority_score = round((1.0 - accuracy) * (1.0 + exam_frequency * 0.2), 2)

    return {
        "accuracy_pct": round(accuracy * 100, 1),
        "status": status,
        "badge_color": color,
        "priority_score": priority_score
    }


def generate_diagnostic_reason(
    topic_name: str,
    correct_count: int,
    total_count: int,
    wrong_questions: List[Dict[str, Any]],
    exam_frequency: int
) -> str:
    """
    Generates a medical-style diagnostic reason for the student's gaps.
    """
    if total_count == 0:
        return f"No diagnostic attempts recorded yet. With {exam_frequency} past exam questions linked, diagnostic evaluation is highly recommended."

    accuracy_pct = round((correct_count / total_count) * 100, 1)

    if accuracy_pct >= 80.0:
        return f"Solid conceptual mastery ({correct_count}/{total_count} correct, {accuracy_pct}%). Key principles are well-retained; minor periodic review advised."

    if not wrong_questions:
        if accuracy_pct < 50.0:
            return f"Significant knowledge deficit ({correct_count}/{total_count} correct). Foundational review required before attempting advanced past papers."
        return f"Partial comprehension ({correct_count}/{total_count} correct). Needs targeted reinforcement on tricky edge cases."

    # Highlight specific failed question concepts
    concepts_missed = []
    for q in wrong_questions[:2]:
        q_text = q.get("question", "")
        citation = q.get("citation", "")
        # Extract a short excerpt
        short = q_text[:70].replace("According to study material on", "").strip()
        concepts_missed.append(f"\"{short}...\" ({citation})")

    missed_summary = "; ".join(concepts_missed)

    if accuracy_pct < 50.0:
        return f"Critical gap: Missed {total_count - correct_count} of {total_count} questions ({accuracy_pct}% accuracy), struggling particularly with: {missed_summary}. Requires step-by-step review."
    else:
        return f"Moderate proficiency ({accuracy_pct}% accuracy). Grasps core definitions but stumbled on specific questions: {missed_summary}."


def build_adaptive_revision_plan(
    topics: List[Dict[str, Any]],
    target_days: int = 5,
    daily_hours: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Creates a dynamic, day-by-day revision schedule tailored to available days and hours.
    Prioritizes topics with highest priority score = (1 - accuracy) * (1 + freq * 0.2).
    """
    target_days = max(1, min(target_days, 30))
    daily_hours = max(0.5, min(daily_hours, 12.0))
    total_study_minutes = int(target_days * daily_hours * 60)
    daily_study_minutes = int(daily_hours * 60)

    # Sort topics strictly by priority score descending
    sorted_topics = sorted(topics, key=lambda t: t.get("priority_score", 0.0), reverse=True)

    total_priority = sum(t.get("priority_score", 0.1) for t in sorted_topics)
    if total_priority == 0:
        total_priority = 1.0

    # Allocate minutes proportional to priority score
    allocated_topics = []
    for t in sorted_topics:
        weight = t.get("priority_score", 0.1) / total_priority
        # Allocate between 30 and 120 minutes per block
        mins = int(round(weight * total_study_minutes))
        mins = max(30, min(mins, 180))
        allocated_topics.append({
            **t,
            "allocated_mins": mins
        })

    # Distribute across target_days
    schedule = []
    current_topic_idx = 0
    num_topics = len(allocated_topics)

    for day_num in range(1, target_days + 1):
        day_blocks = []
        minutes_left_today = daily_study_minutes

        # Populate day with topics
        while minutes_left_today >= 30 and current_topic_idx < num_topics:
            t = allocated_topics[current_topic_idx]
            block_time = min(t["allocated_mins"], minutes_left_today)

            # Determine objective based on status
            status = t.get("status", "Medium")
            if status == "Weak":
                objective = f"Deep dive into foundational concepts & solve 5 grounded problems on {t['name']}."
            elif status == "Medium":
                objective = f"Targeted review of missed nuances and edge cases on {t['name']}."
            else:
                objective = f"Speed revision and quick formula/concept verification on {t['name']}."

            day_blocks.append({
                "time_allocated_minutes": block_time,
                "topic_id": t.get("id", 0),
                "topic_name": t.get("name", "Topic"),
                "status": status,
                "priority_score": t.get("priority_score", 1.0),
                "focus_objective": objective,
                "recommended_source": f"Uploaded Notes (Weightage: {t.get('weightage_level', 'Medium')}, {t.get('exam_frequency', 0)} Exam Qs)",
                "completed": False
            })

            t["allocated_mins"] -= block_time
            minutes_left_today -= block_time

            if t["allocated_mins"] <= 0:
                current_topic_idx += 1

        # If days remain after covering all topics, fill with mock test and synthesis review
        if not day_blocks:
            day_blocks.append({
                "time_allocated_minutes": daily_study_minutes,
                "topic_id": sorted_topics[0]["id"] if sorted_topics else 1,
                "topic_name": "Full Comprehensive Diagnostic Retake & High-Yield Review",
                "status": "Medium",
                "priority_score": 0.5,
                "focus_objective": "Retake full diagnostic battery to verify retention and measure score progression across all modules.",
                "recommended_source": "Past Papers & Consolidated Notes",
                "completed": False
            })

        schedule.append({
            "day": day_num,
            "day_title": f"Day {day_num}: Focus on High-Yield Priority Targets" if day_num <= 2 else f"Day {day_num}: Reinforcement & Verification",
            "total_study_minutes": sum(b["time_allocated_minutes"] for b in day_blocks),
            "blocks": day_blocks
        })

    return schedule
