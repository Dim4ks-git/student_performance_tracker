import math
import unittest
from unittest.mock import Mock

from study_service.schemas import CheckIn
from study_service.scoring import estimate


class EstimateTests(unittest.TestCase):
    def setUp(self):
        self.answers = CheckIn(
            previous_exam_score=73.4,
            study_hours_per_day=3.42,
            practice_tests_completed=0,
        )
        self.predictor = Mock()
        self.predictor.predict.return_value = [71.9617451655]
        self.features = [
            "practice_tests_completed",
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
        ]
        self.bundle = (self.predictor, self.features, "v1")

    def test_predicts_in_bundle_order_with_missing_attendance_and_zero_tests(self):
        self.assertEqual(estimate(self.answers, self.bundle), (71.9617451655, "v1"))
        self.predictor.predict.assert_called_once()
        (frame,) = self.predictor.predict.call_args.args
        self.assertEqual(frame.columns.tolist(), self.features)
        self.assertEqual(len(frame), 1)
        tests, prior_score, attendance, study_hours = frame.iloc[0].tolist()
        self.assertEqual((tests, prior_score, study_hours), (0, 73.4, 3.42))
        self.assertTrue(math.isnan(attendance))

    def test_missing_required_input_skips_prediction(self):
        for field in ("previous_exam_score", "study_hours_per_day", "practice_tests_completed"):
            with self.subTest(field=field):
                answers = self.answers.model_copy(update={field: None})
                self.assertEqual(estimate(answers, self.bundle), (None, None))
                self.predictor.predict.assert_not_called()

    def test_missing_bundle_returns_no_score(self):
        self.assertEqual(estimate(self.answers, None), (None, None))

    def test_clamps_score_to_display_bounds(self):
        for prediction, expected in ((105, 100.0), (-5, 0.0)):
            with self.subTest(prediction=prediction):
                self.predictor.predict.return_value = [prediction]
                self.assertEqual(estimate(self.answers, self.bundle), (expected, "v1"))

    def test_nonfinite_prediction_returns_no_score(self):
        for prediction in (math.nan, math.inf, -math.inf):
            with self.subTest(prediction=prediction):
                self.predictor.predict.return_value = [prediction]
                self.assertEqual(estimate(self.answers, self.bundle), (None, None))

    def test_predictor_value_error_returns_no_score(self):
        self.predictor.predict.side_effect = ValueError("unsupported input")
        self.assertEqual(estimate(self.answers, self.bundle), (None, None))
