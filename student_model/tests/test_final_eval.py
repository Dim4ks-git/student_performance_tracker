import unittest
from unittest.mock import patch, sentinel

from student_model.modeling.final_eval import final_evaluation


class FinalEvaluationTests(unittest.TestCase):
    def setUp(self):
        features = [
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
        ]
        self.run_data = {
            "schema": {"score_features": features, "target": "exam_score"},
            "dataset_sha256": "a" * 64,
            "dev": sentinel.dev,
            "test": sentinel.test,
        }
        self.receipt = {
            "approved": True,
            "dataset_sha256": self.run_data["dataset_sha256"],
            "score_features": features.copy(),
        }

    def test_invalid_receipts_do_not_fit_or_score(self):
        for change in (
            {"approved": False},
            {"approved": 1},
            {"dataset_sha256": "b" * 64},
            {"score_features": self.receipt["score_features"][::-1]},
        ):
            with (
                self.subTest(change=change),
                patch("student_model.modeling.final_eval.fit_models") as fit,
                patch("student_model.modeling.final_eval.compare") as compare,
                patch("student_model.modeling.final_eval.slice_errors") as slice_errors,
            ):
                with self.assertRaises(ValueError):
                    final_evaluation(self.run_data, {**self.receipt, **change})

                fit.assert_not_called()
                compare.assert_not_called()
                slice_errors.assert_not_called()

    def test_approved_receipt_refits_on_dev_and_reuses_holdout_predictions(self):
        models = {
            "score_model": (self.receipt["score_features"], sentinel.ridge),
        }
        with (
            patch("student_model.modeling.final_eval.fit_models", return_value=models) as fit,
            patch(
                "student_model.modeling.final_eval.compare",
                return_value=(sentinel.metrics, sentinel.predictions),
            ) as compare,
            patch("student_model.modeling.final_eval.slice_errors", return_value=sentinel.slices) as slice_errors,
        ):
            result = final_evaluation(self.run_data, self.receipt)

        fit.assert_called_once_with(sentinel.dev, self.run_data["schema"])
        compare.assert_called_once_with(models, sentinel.test, "exam_score")
        slice_errors.assert_called_once_with(sentinel.test, "exam_score", sentinel.predictions)
        self.assertEqual(result, (sentinel.ridge, sentinel.metrics, sentinel.slices))
