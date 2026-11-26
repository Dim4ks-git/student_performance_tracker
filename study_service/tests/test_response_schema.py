import json
import unittest

from pydantic import ValidationError

from study_service.schemas import StudyResult


class StudyResultTests(unittest.TestCase):
    def setUp(self):
        self.response = {
            "estimated_exam_score": None,
            "model_version": None,
            "recommendation": {
                "reason": "You can build on what you remember.",
                "action": "Make a short practice quiz.",
                "follow_up": "Review the questions you missed.",
            },
            "optional_question": None,
        }

    def test_serialization_preserves_null_keys(self):
        result = StudyResult.model_validate(self.response)
        self.assertEqual(json.loads(result.model_dump_json()), self.response)

    def test_nested_follow_up_is_required(self):
        del self.response["recommendation"]["follow_up"]
        with self.assertRaises(ValidationError) as error:
            StudyResult.model_validate(self.response)
        self.assertEqual(error.exception.errors()[0]["loc"], ("recommendation", "follow_up"))

    def test_all_top_level_keys_are_required(self):
        for key in self.response:
            with self.subTest(key=key):
                response = self.response.copy()
                del response[key]
                with self.assertRaises(ValidationError) as error:
                    StudyResult.model_validate(response)
                self.assertEqual(error.exception.errors()[0]["loc"], (key,))

    def test_extra_keys_are_forbidden_at_both_levels(self):
        for response, location in (
            ({**self.response, "extra": True}, ("extra",)),
            (
                {
                    **self.response,
                    "recommendation": {**self.response["recommendation"], "extra": True},
                },
                ("recommendation", "extra"),
            ),
        ):
            with self.subTest(location=location):
                with self.assertRaises(ValidationError) as error:
                    StudyResult.model_validate(response)
                self.assertEqual(error.exception.errors()[0]["loc"], location)

    def test_estimated_score_bounds(self):
        for score in (0.0, 72.5, 100.0):
            with self.subTest(score=score):
                result = StudyResult.model_validate({**self.response, "estimated_exam_score": score})
                self.assertEqual(result.estimated_exam_score, score)

        for score in (-0.1, 100.1):
            with self.subTest(score=score):
                with self.assertRaises(ValidationError) as error:
                    StudyResult.model_validate({**self.response, "estimated_exam_score": score})
                self.assertEqual(error.exception.errors()[0]["loc"], ("estimated_exam_score",))
