"""Choose a study action and optional question from the student's original answers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from study_service.schemas import CheckIn


_TIPS = {
    "make_quiz": (
        "You reported infrequent revision and zero completed practice tests.",
        "Make a five-question quiz from your class notes and try it from memory.",
        "Can you answer the missed questions on another day?",
    ),
    "use_one_test": (
        "You reported infrequent revision and one completed practice test.",
        "Pick one topic from your test. Try five questions from memory, "
        "check them and retry the misses another day.",
        "Can you answer the previously missed questions from memory?",
    ),
    "review_mistakes": (
        "You reported infrequent revision and several completed tests.",
        "Choose two mistakes from earlier tests. On two different days, "
        "explain why the correct answers work.",
        "Can you explain both answers at the second review?",
    ),
    "recall": (
        "You chose help remembering material.",
        "Close your notes and write down three things you remember about one topic.",
        "Which points could you recall a day later?",
    ),
    "coursework": (
        "You chose help finishing coursework.",
        "Pick one assignment and schedule its next small step.",
        "Did you complete that step?",
    ),
    "general": (
        "A short practice session can give you a starting point.",
        "Pick one topic and try recalling it before checking your notes.",
        "Which part would you like help with next?",
    ),
}


def tip_key(
    revision_frequency: str | None,
    practice_tests_completed: int | None,
    goal: str | None,
) -> str:
    """Give an explicit goal priority over observed study habits."""
    if goal == "remember_material":
        return "recall"
    if goal == "finish_coursework":
        return "coursework"

    if revision_frequency == "Rarely" and practice_tests_completed is not None:
        if practice_tests_completed == 0:
            return "make_quiz"
        if practice_tests_completed == 1:
            return "use_one_test"
        if practice_tests_completed >= 2:
            return "review_mistakes"

    return "general"


def recommendation(answers: "CheckIn") -> dict[str, str]:
    """Return one complete study tip based on the original check-in."""
    key = tip_key(
        answers.revision_frequency,
        answers.practice_tests_completed,
        answers.goal,
    )
    reason, action, follow_up = _TIPS[key]
    rate = answers.assignment_completion_rate
    if key == "coursework" and rate is not None:
        reason = f"You reported completing {rate:g}% of assignments due."

    return {"reason": reason, "action": action, "follow_up": follow_up}


def next_question(answers: "CheckIn") -> str | None:
    """Ask for the first missing score input or invite the student to choose a goal."""
    if answers.previous_exam_score is None:
        return "What was your last comparable exam mark out of 100?"
    if answers.study_hours_per_day is None:
        return "How many hours per day did you study?"
    if answers.practice_tests_completed is None:
        return "How many practice tests did you finish?"

    key = tip_key(
        answers.revision_frequency,
        answers.practice_tests_completed,
        answers.goal,
    )
    if key == "general":
        return "Would you like help remembering material or finishing coursework?"
    return None
