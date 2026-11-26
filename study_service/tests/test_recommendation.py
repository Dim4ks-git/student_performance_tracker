import unittest

from study_service.advice import recommendation
from study_service.schemas import CheckIn


class RecommendationTests(unittest.TestCase):
    def test_infrequent_revision_uses_observed_test_count(self):
        cases = (
            (
                0,
                "You reported infrequent revision and zero completed practice tests.",
                "Make a five-question quiz from your class notes and try it from memory.",
                "Can you answer the missed questions on another day?",
            ),
            (
                1,
                "You reported infrequent revision and one completed practice test.",
                "Pick one topic from your test. Try five questions from memory, "
                "check them and retry the misses another day.",
                "Can you answer the previously missed questions from memory?",
            ),
            (
                8,
                "You reported infrequent revision and several completed tests.",
                "Choose two mistakes from earlier tests. On two different days, "
                "explain why the correct answers work.",
                "Can you explain both answers at the second review?",
            ),
        )
        for count, reason, action, follow_up in cases:
            with self.subTest(count=count):
                answers = CheckIn(
                    revision_frequency="Rarely",
                    practice_tests_completed=count,
                )
                self.assertEqual(
                    recommendation(answers),
                    {"reason": reason, "action": action, "follow_up": follow_up},
                )

    def test_empty_check_in_returns_general_tip(self):
        self.assertEqual(
            recommendation(CheckIn()),
            {
                "reason": "A short practice session can give you a starting point.",
                "action": "Pick one topic and try recalling it before checking your notes.",
                "follow_up": "Which part would you like help with next?",
            },
        )

    def test_explicit_recall_goal_takes_priority(self):
        answers = CheckIn(
            goal="remember_material",
            revision_frequency="Rarely",
            practice_tests_completed=0,
            assignment_completion_rate=0,
        )
        self.assertEqual(
            recommendation(answers),
            {
                "reason": "You chose help remembering material.",
                "action": "Close your notes and write down three things you remember about one topic.",
                "follow_up": "Which points could you recall a day later?",
            },
        )

    def test_coursework_reason_uses_observed_rate_or_default(self):
        for rate, reason in (
            (0, "You reported completing 0% of assignments due."),
            (82.5, "You reported completing 82.5% of assignments due."),
            (None, "You chose help finishing coursework."),
        ):
            with self.subTest(rate=rate):
                fields = {"goal": "finish_coursework"}
                if rate is not None:
                    fields["assignment_completion_rate"] = rate
                self.assertEqual(
                    recommendation(CheckIn(**fields)),
                    {
                        "reason": reason,
                        "action": ("Pick one assignment and schedule its next small step." if rate is None
                                   else "Open the unfinished assignment due soonest and schedule its first incomplete step."),
                        "follow_up": "Did you complete that step?",
                    },
                )

    def test_each_call_returns_a_fresh_dictionary(self):
        answers = CheckIn()
        tip = recommendation(answers)
        tip["reason"] = "Changed by caller."
        self.assertEqual(
            recommendation(answers)["reason"],
            "A short practice session can give you a starting point.",
        )

    def test_recalls_with_the_reported_method_and_can_continue_with_only_an_outcome(self):
        first = CheckIn(goal="remember_material", study_method="Flashcards")
        self.assertIn("cards", recommendation(first)["action"])
        later = CheckIn(goal="remember_material", last_check_in={"outcome": "not_tried"})
        self.assertIn("recall just one idea", recommendation(later)["action"])
