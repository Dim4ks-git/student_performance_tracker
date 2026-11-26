import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import joblib

from study_service.scoring import load_bundle


class LoadBundleTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.directory = Path(temporary_directory.name)
        self.pipeline = {"fixture": "trusted joblib payload"}
        self.features = [
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
        ]
        pipeline_path = self.directory / "score_pipeline.joblib"
        joblib.dump(self.pipeline, pipeline_path)
        self.model_version = hashlib.sha256(pipeline_path.read_bytes()).hexdigest()
        (self.directory / "feature_schema.json").write_text(
            json.dumps({"score_features": self.features}), encoding="utf-8"
        )
        self.write_manifest(self.model_version)

    def write_manifest(self, model_version):
        (self.directory / "manifest.json").write_text(
            json.dumps({"model_version": model_version}), encoding="utf-8"
        )

    def test_loads_pipeline_in_schema_order_with_model_version(self):
        self.assertEqual(
            load_bundle(self.directory),
            (self.pipeline, self.features, self.model_version),
        )

    def test_digest_mismatch_fails_before_deserialization(self):
        self.write_manifest("wrong")
        with patch("study_service.scoring.joblib.load") as deserialize:
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                load_bundle(self.directory)
            deserialize.assert_not_called()

    def test_missing_bundle_files_raise_load_error(self):
        for filename in ("manifest.json", "feature_schema.json", "score_pipeline.joblib"):
            with self.subTest(filename=filename):
                path = self.directory / filename
                contents = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaises(FileNotFoundError):
                        load_bundle(self.directory)
                finally:
                    path.write_bytes(contents)
