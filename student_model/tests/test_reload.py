import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import joblib

from student_model.publishing.artifacts import save_model
from student_model.modeling.estimators import make_ridge
from student_model.preprocessing.experiment import load_input


CSV_PATH = Path(__file__).resolve().parents[1] / "datasets" / "student_exam_performance_copy.csv"
PINNED_DATASET_SHA256 = "3967020b770568f9a732387f04907807bf0c39cd1d8c96077e36646387cdf1bc"


class ReloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_data = load_input(CSV_PATH)
        cls.schema = cls.run_data["schema"]
        cls.features = cls.schema["score_features"]

    def _constant_pipeline(self):
        rows = self.run_data["dev"][self.features].head(4)
        return make_ridge().fit(rows, [42] * len(rows))

    def test_round_trip_matches_real_holdout_reference(self):
        self.assertEqual(
            self.run_data["dataset_sha256"],
            "aa3f57815e36a049e2545a7c4efd6c37e22e1fd71b0d6ab6164fb01d460ecc8a",
        )
        dev = self.run_data["dev"]
        target = self.schema["target"]
        pipeline = make_ridge().fit(dev[self.features], dev[target])
        row = self.run_data["test"].loc[[1], self.features + [target]]
        prior, attendance, study_hours, practice_tests, observed = row.iloc[0]
        self.assertTrue(math.isnan(attendance))
        self.assertEqual(observed, 86.21)
        inputs = [prior, None, study_hours, practice_tests]
        self.assertEqual(inputs, [73.4, None, 3.42, 10])
        before = float(pipeline.predict(row[self.features])[0])
        self.assertAlmostEqual(before, 71.9617451655, delta=1e-6)

        with tempfile.TemporaryDirectory() as directory:
            save_model(directory, pipeline, self.schema, self.run_data["dataset_sha256"])
            bundle = Path(directory)
            schema = json.loads((bundle / "feature_schema.json").read_text(encoding="utf-8"))
            reference = json.loads((bundle / "reference.json").read_text(encoding="utf-8"))
            restored = joblib.load(bundle / "score_pipeline.joblib")
            after = float(restored.predict(row[schema["score_features"]])[0])

        self.assertEqual(schema, self.schema)
        self.assertEqual(reference, {"input": inputs, "expected": before, "atol": 1e-6})
        self.assertAlmostEqual(after, before, delta=1e-6)

    def test_constant_target_round_trip_with_unpinned_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            save_model(directory, self._constant_pipeline(), self.schema, "a" * 64)
            reference_path = Path(directory) / "reference.json"
            reference = json.loads(reference_path.read_text(encoding="utf-8"))

        self.assertEqual(reference["expected"], 42.0)

    def test_constant_target_fails_published_reference_check(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "published reference"):
                save_model(directory, self._constant_pipeline(), self.schema, PINNED_DATASET_SHA256)
            self.assertFalse((Path(directory) / "reference.json").exists())

    def test_reloaded_prediction_mismatch_raises(self):
        reloaded = Mock()
        reloaded.predict.return_value = [43.0]
        with tempfile.TemporaryDirectory() as directory:
            with patch("student_model.publishing.artifacts.joblib.load", return_value=reloaded):
                with self.assertRaisesRegex(ValueError, "pre-save reference"):
                    save_model(directory, self._constant_pipeline(), self.schema, "a" * 64)
            self.assertFalse((Path(directory) / "reference.json").exists())
