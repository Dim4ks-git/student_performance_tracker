import unittest
from unittest.mock import patch, sentinel

from student_model.validate import validation_report


class ValidationReportTests(unittest.TestCase):
    def test_validation_decision_uses_unrounded_gain_and_only_validation_rows(self):
        score_features = [
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
        ]
        schema = {"score_features": score_features, "target": "exam_score"}
        run = {
            "schema": schema,
            "dataset_sha256": "a" * 64,
            "train": sentinel.train,
            "validation": sentinel.validation,
        }

        for median_mae, previous_mae, ridge_mae, gain, approved in (
            (12, 11, 10, 1.0, True),
            (12, 11, 10.01, 0.99, False),
            (12, 11, 10.001, 0.999, False),
            (11, 12, 10, 1.0, True),
        ):
            with self.subTest(median=median_mae, previous=previous_mae, ridge4=ridge_mae):
                metrics = {
                    "median": {"mae": median_mae, "rmse": 13},
                    "previous": {"mae": previous_mae, "rmse": 13},
                    "ridge4": {"mae": ridge_mae, "rmse": 11},
                }
                with (
                    patch("student_model.validate.fit_models", return_value=sentinel.models) as fit,
                    patch(
                        "student_model.validate.compare",
                        return_value=(metrics, sentinel.predictions),
                    ) as compare,
                ):
                    report = validation_report(run)

                fit.assert_called_once_with(sentinel.train, schema)
                compare.assert_called_once_with(sentinel.models, sentinel.validation, "exam_score")
                self.assertEqual(
                    set(report), {"dataset_sha256", "score_features", "metrics", "gain_mae", "approved"}
                )
                self.assertEqual(report["dataset_sha256"], run["dataset_sha256"])
                self.assertEqual(report["score_features"], score_features)
                self.assertEqual(report["metrics"], metrics)
                self.assertAlmostEqual(report["gain_mae"], gain)
                self.assertIs(report["approved"], approved)
