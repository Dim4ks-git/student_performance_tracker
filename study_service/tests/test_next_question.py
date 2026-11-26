import unittest

from study_service.advice import next_question
from study_service.schemas import CheckIn


class NextQuestionTests(unittest.TestCase):
    def test_asks_for_first_missing_score_input(self):
        cases = (
            (CheckIn(), "What was your last comparable exam mark out of 100?"),
            (CheckIn(previous_exam_score=0), "How many hours per day did you study?"),
            (
                CheckIn(previous_exam_score=73.4, study_hours_per_day=0),
                "How many practice tests did you finish?",
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

    def test_selected_goal_needs_no_question_when_score_inputs_are_present(self):
        answers = CheckIn(
            previous_exam_score=73.4,
            study_hours_per_day=3.42,
            practice_tests_completed=0,
            goal="remember_material",
        )
        self.assertIsNone(next_question(answers))
