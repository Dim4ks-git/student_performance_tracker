import math
import unittest

import pandas as pd

from student_model.evaluation import slice_errors


class SliceErrorsTests(unittest.TestCase):
    def setUp(self):
        self.rows = pd.DataFrame(
            {
                "attendance_percentage": [0] + [90] * 29 + [float("nan")],
                "education_level": pd.Categorical(
                    ["A"] * 30 + ["B"], categories=["A", "B", "unused"]
                ),
                "exam_score": [10] * 31,
            },
            index=range(100, 38, -2),
        )
        self.predictions = pd.Series(
            [10] * 30 + [14], index=self.rows.index
        ).iloc[::-1]

    def test_reports_attendance_and_observed_education_cohorts(self):
        result = slice_errors(self.rows, "exam_score", self.predictions)

        self.assertEqual(
            result,
            {
                "attendance_present": {"n": 30, "mae": 0.0, "rmse": 0.0},
                "attendance_missing": {"n": 1, "mae": 4.0, "rmse": 4.0},
                "education_level": {
                    "A": {"n": 30, "mae": 0.0, "rmse": 0.0},
                    "B": {"n": 1, "mae": None, "rmse": None},
                },
            },
        )

    def test_empty_missing_attendance(self):
        self.rows["attendance_percentage"] = 90

        result = slice_errors(self.rows, "exam_score", self.predictions)

        self.assertEqual(
            result["attendance_missing"], {"n": 0, "mae": None, "rmse": None}
        )
        self.assertEqual(result["attendance_present"]["n"], 31)
        self.assertAlmostEqual(result["attendance_present"]["mae"], 4 / 31)
        self.assertAlmostEqual(result["attendance_present"]["rmse"], math.sqrt(16 / 31))

    def test_omits_missing_education(self):
        self.rows.loc[self.rows.index[-1], "education_level"] = None

        result = slice_errors(self.rows, "exam_score", self.predictions)

        self.assertEqual(result["education_level"], {"A": {"n": 30, "mae": 0.0, "rmse": 0.0}})
