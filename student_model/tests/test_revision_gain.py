import unittest

import pandas as pd

from student_model.candidate_fields import revision_gain


class RevisionGainTests(unittest.TestCase):
    def test_unseen_revision_frequency_has_zero_gain_for_constant_target(self):
        features = [
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
        ]
        schema = {"score_features": features.copy(), "target": "observed_mark"}
        rows = pd.DataFrame(
            {
                "previous_exam_score": range(50, 80),
                "attendance_percentage": 80,
                "study_hours_per_day": 2,
                "practice_tests_completed": 1,
                "revision_frequency": ["Weekly"] * 25 + ["Daily"] * 5,
                "observed_mark": 50,
            }
        )
        run = {"schema": schema, "train": rows.iloc[:25], "validation": rows.iloc[25:]}

        self.assertEqual(revision_gain(run), 0.0)
        self.assertEqual(schema, {"score_features": features, "target": "observed_mark"})
