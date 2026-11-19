import unittest

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from student_model.estimators import make_ridge


class MakeRidgeTests(unittest.TestCase):
    def setUp(self):
        self.features = pd.DataFrame(
            [[0, 10], [1, float("nan")], [2, 30]],
            columns=["first", "second"],
        )
        self.targets = [10, 20, 30]

    def test_pipeline_steps_and_parameters(self):
        pipeline = make_ridge()

        self.assertIsInstance(pipeline, Pipeline)
        self.assertEqual(list(pipeline.named_steps), ["impute", "scale", "ridge"])
        self.assertIsInstance(pipeline.named_steps.impute, SimpleImputer)
        self.assertEqual(pipeline.named_steps.impute.strategy, "median")
        self.assertIsInstance(pipeline.named_steps.scale, StandardScaler)
        self.assertIsInstance(pipeline.named_steps.ridge, Ridge)
        self.assertEqual(pipeline.named_steps.ridge.alpha, 1.0)

    def test_prediction_preserves_training_statistics(self):
        pipeline = make_ridge().fit(self.features, self.targets)
        imputer = pipeline.named_steps.impute
        scaler = pipeline.named_steps.scale

        self.assertEqual(imputer.statistics_[1], 20)
        self.assertEqual(scaler.mean_[1], 20)

        prediction_row = pd.DataFrame([[100, 9999]], columns=self.features.columns)
        self.assertEqual(pipeline.predict(prediction_row).shape, (1,))

        self.assertEqual(imputer.statistics_[1], 20)
        self.assertEqual(scaler.mean_[1], 20)

    def test_each_call_returns_a_fresh_unfitted_pipeline(self):
        fitted = make_ridge().fit(self.features, self.targets)
        fresh = make_ridge()

        self.assertIsNot(fresh, fitted)
        for name, step in fresh.steps:
            self.assertIsNot(step, fitted.named_steps[name])
        self.assertFalse(hasattr(fresh.named_steps.impute, "statistics_"))
        self.assertFalse(hasattr(fresh.named_steps.scale, "mean_"))
        self.assertFalse(hasattr(fresh.named_steps.ridge, "coef_"))
