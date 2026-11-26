import unittest

from pydantic import ValidationError

from study_service.schemas import CheckIn


class CheckInTests(unittest.TestCase):
    def test_omitted_and_null_answers_are_supported(self):
        unanswered = dict.fromkeys((
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
            "revision_frequency",
            "assignment_completion_rate",
            "goal",
        ))
        self.assertEqual(CheckIn.model_validate({}).model_dump(), unanswered)
        self.assertEqual(CheckIn.model_validate(unanswered).model_dump(), unanswered)

    def test_partial_check_in_preserves_observed_zero(self):
        check_in = CheckIn.model_validate_json(
            '{"study_hours_per_day":3.42,"practice_tests_completed":0,'
            '"attendance_percentage":null}'
        )
        self.assertEqual(check_in.study_hours_per_day, 3.42)
        self.assertEqual(check_in.practice_tests_completed, 0)
        self.assertIsNone(check_in.attendance_percentage)

    def test_valid_bounds_and_choices(self):
        for revision, goal in (
            ("Rarely", "remember_material"),
            ("Weekly", "finish_coursework"),
            ("Daily", None),
        ):
            with self.subTest(revision=revision, goal=goal):
                check_in = CheckIn(
                    previous_exam_score=0,
                    attendance_percentage=100,
                    study_hours_per_day=24,
                    practice_tests_completed=8,
                    revision_frequency=revision,
                    assignment_completion_rate=100,
                    goal=goal,
                )
                self.assertEqual(check_in.revision_frequency, revision)
                self.assertEqual(check_in.goal, goal)

    def test_invalid_answers_are_rejected(self):
        for field, value in (
            ("attendance_percentage", 101),
            ("practice_tests_completed", 1.5),
            ("practice_tests_completed", True),
            ("study_hours_per_day", 25),
            ("revision_frequency", "rarely"),
            ("exam_score", 80),
            ("previous_exam_score", -1),
            ("assignment_completion_rate", 101),
            ("practice_tests_completed", -1),
            ("study_hours_per_day", "3.42"),
            ("attendance_percentage", float("nan")),
            ("study_hours_per_day", float("inf")),
            ("goal", "raise_score"),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValidationError) as error:
                    CheckIn.model_validate({field: value})
                self.assertEqual(error.exception.errors()[0]["loc"], (field,))
