import unittest

from study_service.advice import next_question
from study_service.schemas import CheckIn


class NextQuestionTests(unittest.TestCase):
    def test_habit_tip_can_prompt_for_missing_score_inputs(self):
        cases = (
            (
                CheckIn(revision_frequency="Rarely", practice_tests_completed=0),
                "What was your last comparable exam mark out of 100?",
            ),
            (
                CheckIn(previous_exam_score=0, revision_frequency="Rarely", practice_tests_completed=1),
                "How many hours per day did you study?",
            ),
        )
        for answers, expected in cases:
            with self.subTest(answers=answers):
                self.assertEqual(next_question(answers), expected)

    def test_general_tip_prompts_for_a_goal(self):
        answers = CheckIn(
            previous_exam_score=73.4,
            study_hours_per_day=3.42,
            practice_tests_completed=0,
        )
        self.assertEqual(
            next_question(answers),
            "Would you like help remembering material or finishing coursework?",
        )

    def test_habit_tip_needs_no_question_even_if_attendance_is_missing(self):
        for attendance in (None, 90):
            with self.subTest(attendance=attendance):
                answers = CheckIn(
                    previous_exam_score=73.4,
                    attendance_percentage=attendance,
                    study_hours_per_day=3.42,
                    practice_tests_completed=0,
                    revision_frequency="Rarely",
                )
                self.assertIsNone(next_question(answers))

    def test_recall_goal_asks_for_method_until_known(self):
        answers = CheckIn(
            previous_exam_score=73.4,
            study_hours_per_day=3.42,
            practice_tests_completed=0,
            goal="remember_material",
        )
        self.assertEqual(next_question(answers), "How do you usually study this material?")
        self.assertIsNone(next_question(answers.model_copy(update={"study_method": "Flashcards"})))
