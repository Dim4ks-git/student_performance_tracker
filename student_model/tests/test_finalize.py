import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib

from student_model import finalize
from student_model.experiment import load_input
from student_model.validate import validation_report


CSV_PATH = Path(__file__).resolve().parents[1] / "student_exam_performance_copy.csv"
DATASET_SHA256 = "aa3f57815e36a049e2545a7c4efd6c37e22e1fd71b0d6ab6164fb01d460ecc8a"


class PublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = validation_report(load_input(CSV_PATH))

    def setUp(self):
        self.parent = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.output = self.parent / "published"
        self.receipt_path = self.parent / "validation.json"
        self.receipt_path.write_text(json.dumps(self.receipt), encoding="utf-8")

    def test_publish_real_bundle_and_reject_retry_without_evaluation(self):
        with patch.object(finalize, "final_evaluation", wraps=finalize.final_evaluation) as evaluate:
            self.assertEqual(finalize.publish(CSV_PATH, self.receipt_path, self.output), self.output)
            original = {path.name: path.read_bytes() for path in self.output.iterdir()}
            with self.assertRaises(FileExistsError):
                finalize.publish(CSV_PATH, self.receipt_path, self.output)
            evaluate.assert_called_once()

        self.assertEqual({path.name: path.read_bytes() for path in self.output.iterdir()}, original)
        self.assertEqual(set(original), {
            "score_pipeline.joblib", "feature_schema.json", "reference.json",
            "metrics.json", "manifest.json",
        })
        self.assertEqual(set(self.parent.iterdir()), {self.receipt_path, self.output})

        manifest = json.loads(original["manifest.json"])
        self.assertEqual(manifest["dataset_sha256"], DATASET_SHA256)
        self.assertEqual(manifest["student_counts"], {
            "dev": 80000, "train": 60000, "validation": 20000, "test": 20000,
        })
        self.assertEqual(manifest["model_version"], hashlib.sha256(original["score_pipeline.joblib"]).hexdigest())

        metrics = json.loads(original["metrics.json"])
        self.assertEqual(metrics["validation"], self.receipt)
        self.assertIs(metrics["validation"]["approved"], True)
        self.assertAlmostEqual(metrics["validation"]["gain_mae"], 1.5212920271, delta=1e-6)
        self.assertAlmostEqual(metrics["test"]["ridge4"]["mae"], 9.4482121269, delta=1e-6)
        self.assertAlmostEqual(metrics["test"]["ridge4"]["rmse"], 11.8910655879, delta=1e-6)
        self.assertEqual(metrics["slices"]["attendance_missing"]["n"], 1979)

        reference = json.loads(original["reference.json"])
        self.assertEqual(reference["input"], [73.4, None, 3.42, 10])
        self.assertAlmostEqual(reference["expected"], 71.9617451655, delta=1e-6)
        self.assertTrue(hasattr(joblib.load(self.output / "score_pipeline.joblib"), "predict"))

    def test_last_writer_failure_removes_staging_and_leaves_output_absent(self):
        def fail_after_writing(bundle, receipt, test_metrics, slices):
            self.assertEqual(bundle.parent.parent, self.parent)
            self.assertFalse(self.output.exists())
            self.assertEqual({path.name for path in bundle.iterdir()}, {
                "score_pipeline.joblib", "feature_schema.json", "reference.json", "manifest.json",
            })
            real_write_metrics(bundle, receipt, test_metrics, slices)
            raise OSError("metrics write failed")

        real_write_metrics = finalize.write_metrics
        with patch.object(finalize, "write_metrics", side_effect=fail_after_writing):
            with self.assertRaisesRegex(OSError, "metrics write failed"):
                finalize.publish(CSV_PATH, self.receipt_path, self.output)

        self.assertEqual(set(self.parent.iterdir()), {self.receipt_path})

    def test_missing_parent_fails_before_evaluation(self):
        with patch.object(finalize, "final_evaluation") as evaluate:
            with self.assertRaises(NotADirectoryError):
                finalize.publish(CSV_PATH, self.receipt_path, self.output / "bundle")
        evaluate.assert_not_called()
