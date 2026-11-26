import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from student_model.preprocessing.numeric import numeric_column


class NumericColumnTests(unittest.TestCase):
    def test_preserves_zero_index_and_name_and_maps_missing_tokens(self):
        values = pd.Series(
            ["0", "NULL", "", "2"],
            index=pd.Index([8, 2, 2, 5], name="record"),
            name="practice_tests_completed",
        )
        expected = pd.Series(
            [0.0, np.nan, np.nan, 2.0], index=values.index, name=values.name
        )

        assert_series_equal(numeric_column(values, lo=0, whole=True), expected)

    def test_rejects_invalid_practice_test_counts(self):
        for invalid in ("-1", "1.5", "inf", "abc"):
            with self.subTest(value=invalid):
                values = pd.Series(["0", invalid], name="practice_tests_completed")

                with self.assertRaisesRegex(ValueError, "practice_tests_completed"):
                    numeric_column(values, lo=0, whole=True)

    def test_accepts_attendance_at_both_bounds_and_preserves_fraction(self):
        values = pd.Series(["0", "81.49", "100"], name="attendance_percentage")
        expected = pd.Series([0.0, 81.49, 100.0], name=values.name)

        assert_series_equal(numeric_column(values, lo=0, hi=100), expected)

    def test_rejects_attendance_above_upper_bound(self):
        values = pd.Series(["101"], name="attendance_percentage")

        with self.assertRaisesRegex(ValueError, "attendance_percentage"):
            numeric_column(values, lo=0, hi=100)
