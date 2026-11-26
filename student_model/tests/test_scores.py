import math
import unittest
from unittest.mock import Mock

import pandas as pd

from student_model.modeling.evaluation import compare, errors


class ScoresTests(unittest.TestCase):
    def test_errors_preserve_fractional_predictions(self):
        metrics = errors([2, 6], [2, 2.5])

        self.assertEqual(metrics["mae"], 1.75)
        self.assertAlmostEqual(metrics["rmse"], math.sqrt(6.125))
        self.assertIs(type(metrics["mae"]), float)
        self.assertIs(type(metrics["rmse"]), float)

    def test_compare_scores_each_model_once_on_the_same_rows(self):
        rows = pd.DataFrame(
            {
                "previous_exam_score": [4, 5],
                "attendance_percentage": [80, 90],
                "study_hours_per_day": [1, 2],
                "practice_tests_completed": [0, 1],
                "exam_score": [2, 6],
            },
            index=[8, 3],
        )
        previous_columns = ["previous_exam_score"]
        ridge_columns = [
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
        ]
        models = {
            "median": (previous_columns, Mock(predict=Mock(return_value=[2, 2]))),
            "previous": (previous_columns, Mock(predict=Mock(return_value=[2, 2]))),
            "score_model": (ridge_columns, Mock(predict=Mock(return_value=[2, 2]))),
        }

        metrics, predictions = compare(models, rows, "exam_score")

        self.assertEqual(set(metrics), set(models))
        for name, (columns, estimator) in models.items():
            with self.subTest(model=name):
                self.assertEqual(metrics[name]["mae"], 2.0)
                self.assertAlmostEqual(metrics[name]["rmse"], math.sqrt(8))
                estimator.predict.assert_called_once()
                pd.testing.assert_frame_equal(
                    estimator.predict.call_args.args[0], rows[columns]
                )
        pd.testing.assert_series_equal(predictions, pd.Series([2, 2], index=rows.index))
