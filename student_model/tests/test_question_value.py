import unittest
from unittest.mock import Mock, patch

import pandas as pd

from student_model.question_value import question_value


class QuestionValueTests(unittest.TestCase):
    @patch("student_model.question_value.permutation_importance")
    @patch("student_model.question_value.fit_models")
    def test_fits_on_train_and_measures_importance_on_validation(
        self, fit_models, permutation_importance
    ):
        expected = {
            "previous_exam_score": 3.5,
            "attendance_percentage": 0.3,
            "study_hours_per_day": 1.3,
            "practice_tests_completed": 0.8,
        }
        columns = list(expected)
        target = "observed_mark"
        schema = {"score_features": columns, "target": target, "group_key": "student_id"}
        train = pd.DataFrame([[60, 80, 2, 0, 70]], columns=columns + [target])
        validation = pd.DataFrame(
            {target: [80], **dict(zip(columns, [72, None, 3, 1]))}, index=[5]
        )
        estimator = Mock()
        fit_models.return_value = {"ridge4": (columns, estimator)}
        permutation_importance.return_value.importances_mean = list(expected.values())

        result = question_value({"train": train, "validation": validation, "schema": schema})

        self.assertEqual(list(result.items()), list(expected.items()))
        fit_models.assert_called_once_with(train, schema)
        permutation_importance.assert_called_once()
        fitted, features, observed = permutation_importance.call_args.args
        self.assertIs(fitted, estimator)
        pd.testing.assert_frame_equal(features, validation[columns])
        pd.testing.assert_series_equal(observed, validation[target])
        self.assertEqual(
            permutation_importance.call_args.kwargs,
            {"scoring": "neg_mean_absolute_error", "n_repeats": 5, "random_state": 23},
        )
