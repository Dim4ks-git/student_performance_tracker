import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from student_model.evaluation import slice_errors
from student_model.experiment import load_input
from student_model.final_eval import final_evaluation
from student_model.reporting import write_metrics
from student_model.validate import validation_report


class MetricsFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        csv_path = Path(__file__).resolve().parents[1] / "student_exam_performance_copy.csv"
        cls.run_data = load_input(csv_path)
        cls.receipt = validation_report(cls.run_data)
        cls.pipeline, cls.test_metrics, cls.slices = final_evaluation(cls.run_data, cls.receipt)

    def test_writes_complete_document_from_csv(self):
        self.assertEqual(
            self.receipt["dataset_sha256"],
            "aa3f57815e36a049e2545a7c4efd6c37e22e1fd71b0d6ab6164fb01d460ecc8a",
        )
        self.assertIs(self.receipt["approved"], True)
        self.assertAlmostEqual(self.receipt["gain_mae"], 1.5212920271133061, places=8)
        expected_metrics = {
            "median": (12.676953, 15.84869583845939),
            "previous": (11.003972940047582, 13.789410195881391),
            "ridge4": (9.448212126904693, 11.891065587943656),
        }
        self.assertEqual(self.test_metrics.keys(), expected_metrics.keys())
        for name, (mae, rmse) in expected_metrics.items():
            with self.subTest(model=name):
                self.assertAlmostEqual(self.test_metrics[name]["mae"], mae, places=8)
                self.assertAlmostEqual(self.test_metrics[name]["rmse"], rmse, places=8)

        self.assertEqual(self.slices["attendance_present"]["n"], 18021)
        self.assertEqual(self.slices["attendance_missing"]["n"], 1979)
        self.assertEqual(
            {name: cohort["n"] for name, cohort in self.slices["education_level"].items()},
            {"High School": 11980, "Undergraduate": 8020},
        )

        with TemporaryDirectory() as directory:
            write_metrics(directory, self.receipt, self.test_metrics, self.slices)
            output = Path(directory) / "metrics.json"
            self.assertEqual(list(Path(directory).iterdir()), [output])
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                {
                    "validation": self.receipt,
                    "test": self.test_metrics,
                    "slices": self.slices,
                    "suitability": "synthetic_demo_only",
                },
            )

    def test_preserves_null_errors_for_empty_and_small_csv_slices(self):
        rows = self.run_data["test"].dropna(subset=["attendance_percentage", "education_level"])
        rows = rows.iloc[:1]
        target = self.run_data["schema"]["target"]
        features = self.receipt["score_features"]
        predictions = pd.Series(self.pipeline.predict(rows[features]), index=rows.index)
        slices = slice_errors(rows, target, predictions)

        with TemporaryDirectory() as directory:
            write_metrics(directory, self.receipt, self.test_metrics, slices)
            report = json.loads((Path(directory) / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(
                report["slices"]["attendance_missing"], {"n": 0, "mae": None, "rmse": None}
            )
            cohort = rows["education_level"].iloc[0]
            self.assertEqual(
                report["slices"]["education_level"][cohort], {"n": 1, "mae": None, "rmse": None}
            )

    def test_rejects_nonfinite_metrics(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), TemporaryDirectory() as directory:
                invalid_metrics = {
                    **self.test_metrics,
                    "ridge4": {**self.test_metrics["ridge4"], "mae": value},
                }
                with self.assertRaises(ValueError):
                    write_metrics(directory, self.receipt, invalid_metrics, self.slices)
                self.assertEqual(list(Path(directory).iterdir()), [])
