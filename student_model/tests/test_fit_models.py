import json
import unittest
from pathlib import Path

import pandas as pd

from student_model.modeling.estimators import fit_models


class FitModelsTests(unittest.TestCase):
    def test_fits_models_on_their_ordered_feature_sets(self):
        schema_path = Path(__file__).resolve().parents[1] / "preprocessing" / "feature_schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        rows = pd.DataFrame(
            {
                "previous_exam_score": [10, 20, 30],
                "attendance_percentage": [80, 90, None],
                "study_hours_per_day": [1, 2, 3],
                "practice_tests_completed": [0, 1, 2],
                "exam_score": [10, 20, 100],
                "pass_status": ["fail", "fail", "pass"],
            }
        )

        models = fit_models(rows, schema)

        self.assertEqual(set(models), {"median", "previous", "ridge4"})
        median_columns, median = models["median"]
        self.assertEqual(median_columns, ["previous_exam_score"])
        self.assertEqual(median.predict(rows[median_columns]).tolist(), [20, 20, 20])

        previous_columns, previous = models["previous"]
        self.assertEqual(previous_columns, ["previous_exam_score"])
        self.assertEqual(previous.feature_names_in_.tolist(), previous_columns)

        ridge_columns, ridge = models["ridge4"]
        self.assertEqual(ridge_columns, schema["score_features"])
        self.assertEqual(ridge.feature_names_in_.tolist(), ridge_columns)
