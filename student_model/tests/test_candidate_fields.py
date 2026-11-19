import unittest

import pandas as pd

from student_model.candidate_fields import assignment_gain


class AssignmentGainTests(unittest.TestCase):
    def test_constant_target_has_zero_gain_and_preserves_score_features(self):
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
                "assignment_completion_rate": 90,
                "observed_mark": 50,
            }
        )
        run = {"schema": schema, "train": rows.iloc[:25], "validation": rows.iloc[25:]}

        self.assertEqual(assignment_gain(run), 0.0)
        self.assertEqual(schema["score_features"], features)
