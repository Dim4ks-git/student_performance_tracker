import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from student_model.preprocessing.csv_input import eligible


class EligibleTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame(
            {"student_id": ["s", "s", "t"], "exam_score": [0, 5, None]},
            index=[8, 2, 5],
        )

    def test_keeps_zero_and_distinct_records_for_one_student_in_order(self):
        original = self.frame.copy()

        result = eligible(self.frame, "student_id", "exam_score")

        assert_frame_equal(result, original.iloc[:2])
        assert_frame_equal(self.frame, original)

    def test_checks_duplicates_across_all_columns(self):
        frame = self.frame.assign(study_hours_per_day=[1, 2, 3])
        frame.at[2, "exam_score"] = 0
        assert_frame_equal(eligible(frame, "student_id", "exam_score"), frame.iloc[:2])

        duplicated = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "Duplicate rows"):
            eligible(duplicated, "student_id", "exam_score")

    def test_rejects_missing_or_blank_group_ids_even_without_a_target(self):
        for value in (None, "", " \t"):
            with self.subTest(value=value):
                frame = self.frame.copy()
                frame.at[5, "student_id"] = value
                with self.assertRaisesRegex(ValueError, "student_id"):
                    eligible(frame, "student_id", "exam_score")

    def test_rejects_a_missing_group_column(self):
        with self.assertRaisesRegex(ValueError, "student_id"):
            eligible(self.frame.drop(columns="student_id"), "student_id", "exam_score")

    def test_rejects_frames_with_no_observed_target(self):
        frame = self.frame.assign(student_id=["s", "t", "u"], exam_score=None)
        for candidate in (frame, frame.iloc[:0]):
            with self.subTest(row_count=len(candidate)):
                with self.assertRaisesRegex(ValueError, "no eligible rows"):
                    eligible(candidate, "student_id", "exam_score")
