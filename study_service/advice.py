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


_OUTCOME_REASONS = {
    "helped": "You said the last step helped.",
    "did_not_help": "You tried the last step and it didn't help.",
    "not_tried": "You haven't tried the last step yet.",
}

# Each pair gives the next action and a question to revisit after trying it.
_NEXT_STEPS = {
    "remember_material": {
        "helped": ("Use the same technique on a second topic, then revisit the first from memory.",
                   "Which parts of both topics could you recall the next day?"),
        "did_not_help": ("Take one point you missed. Work through an example, then cover it and explain it in your own words.",
                         "Could you explain that point without the example?"),
        "not_tried": ("At the end of your next class, close your notes and recall just one idea.",
                      "Did you get a chance to recall that idea?"),
    },
    "finish_coursework": {
        "helped": ("Use the approach that worked on the next unfinished part of your assignment. Set aside time for it today.",
                   "What part did you finish in that session?"),
        "did_not_help": ("Find the first instruction you are stuck on and write one specific question to take to your teacher or study group.",
                         "Did the answer let you continue the assignment?"),
        "not_tried": ("Open the assignment due soonest and write down the first thing it asks you to do.",
                      "Were you able to identify a starting point?"),
    },
    None: {
        "helped": ("Try the step that worked on one more topic or task.",
                   "Did it help with the second task too?"),
        "did_not_help": ("Write down the first point where you got stuck and take that question to your next class.",
                         "Did the answer help you move on?"),
        "not_tried": ("Choose a two-minute version of the step and a time today to try it.",
                      "Did you find time to try the shorter step?"),
    },
}

_RECALL_BY_METHOD = {
    "Self-Reading": "After reading one section, cover it and write two questions you can answer from memory.",
    "Summarizing": "Cover your summary and reconstruct its three main points before checking it.",
    "Flashcards": "Set aside two cards you missed and answer them again tomorrow before turning them over.",
    "Group Study": "Ask a study partner to quiz you on one topic, then switch roles.",
    "Practice Tests": "Pick a missed test question and explain the answer from memory before checking the solution.",
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
    """Use prior feedback for the same goal, or start fresh when the goal changes."""
    goal = answers.coaching_goal
    outcome = answers.previous_outcome
    if outcome:
        action, follow_up = _NEXT_STEPS[goal][outcome]
        return {"reason": _OUTCOME_REASONS[outcome], "action": action, "follow_up": follow_up}

    key = tip_key(
        answers.revision_frequency,
        answers.practice_tests_completed,
        goal,
    )
    reason, action, follow_up = _TIPS[key]
    rate = answers.assignment_completion_rate
    if key == "coursework" and rate is not None:
        reason = f"You reported completing {rate:g}% of assignments due."
        if rate == 100:
            action = "Look at the next assignment due and set a reminder for its first step."
        else:
            action = "Open the unfinished assignment due soonest and schedule its first incomplete step."
    if key == "recall" and answers.study_method:
        reason = f"You use {answers.study_method.lower()} and want to remember material."
        action = _RECALL_BY_METHOD[answers.study_method]

    return {"reason": reason, "action": action, "follow_up": follow_up}


def next_question(answers: "CheckIn") -> str | None:
    """Ask one question relevant to the current coaching goal."""
    goal = answers.coaching_goal
    if goal:
        if answers.previous_outcome:
            return None
        if goal == "remember_material" and answers.study_method is None:
            return "How do you usually study this material?"
        if goal == "finish_coursework" and answers.assignment_completion_rate is None:
            return "What percentage of assignments due have you completed?"
        return None
    if tip_key(answers.revision_frequency, answers.practice_tests_completed, goal) == "general":
        return "Would you like help remembering material or finishing coursework?"
    if answers.previous_exam_score is None:
        return "What was your last comparable exam mark out of 100?"
    if answers.study_hours_per_day is None:
        return "How many hours per day did you study?"
    return None
