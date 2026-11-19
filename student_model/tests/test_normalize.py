import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from student_model.data import HEADER, normalize


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame("", index=[8, 2], columns=HEADER)
        self.raw["attendance_percentage"] = ["", "NULL"]
        self.raw["practice_tests_completed"] = ["0", "4"]
        self.raw["study_hours_per_day"] = ["3.42", "0"]
        self.raw["student_id"] = ["001", "002"]
        self.raw["school_type"] = ["Public, charter", "NULL"]
        self.raw["education_level"] = ["High School", ""]

    def test_normalizes_missing_tokens_and_preserves_observed_values(self):
        original = self.raw.copy()
        normalized = normalize(self.raw)

        self.assertTrue(normalized["attendance_percentage"].isna().all())
        self.assertEqual(normalized["practice_tests_completed"].tolist(), [0.0, 4.0])
        self.assertEqual(normalized["study_hours_per_day"].tolist(), [3.42, 0.0])
        self.assertEqual(normalized["student_id"].tolist(), ["001", "002"])
        self.assertEqual(normalized.at[8, "school_type"], "Public, charter")
        self.assertEqual(normalized.at[8, "education_level"], "High School")
        self.assertTrue(pd.isna(normalized.at[2, "school_type"]))
        self.assertTrue(pd.isna(normalized.at[2, "education_level"]))
        self.assertTrue(normalized.index.equals(self.raw.index))
        self.assertEqual(tuple(normalized.columns), HEADER)
        assert_frame_equal(self.raw, original)

    def test_rejects_invalid_numeric_values_with_column_name(self):
        for column, value in (
            ("attendance_percentage", "101"),
            ("practice_tests_completed", "1.5"),
            ("study_hours_per_day", "25"),
            ("study_hours_per_day", "inf"),
            ("study_hours_per_day", "abc"),
        ):
            with self.subTest(column=column, value=value):
                raw = self.raw.copy()
                raw.at[8, column] = value

                with self.assertRaisesRegex(ValueError, column):
                    normalize(raw)
