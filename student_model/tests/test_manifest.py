import hashlib
import json
import platform
import tempfile
import unittest
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from student_model.artifacts import write_manifest


class ManifestTests(unittest.TestCase):
    def test_records_model_identity_runtime_and_grouped_split(self):
        model_bytes = b"staged pipeline fixture\x00\xff"
        dataset_sha256 = "a" * 64
        run = {
            "dataset_sha256": dataset_sha256,
            "schema": {"group_key": "learner_id"},
            "dev": pd.DataFrame({"learner_id": [1, 1, 2, 3, 4, 4]}),
            "train": pd.DataFrame({"learner_id": [1, 1, 2, 3]}),
            "validation": pd.DataFrame({"learner_id": [4, 4]}),
            "test": pd.DataFrame({"learner_id": [5, 5, 6]}),
        }

        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            (bundle / "score_pipeline.joblib").write_bytes(model_bytes)
            write_manifest(bundle, run)
            manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["dataset_sha256"], dataset_sha256)
        self.assertEqual(manifest["model_version"], hashlib.sha256(model_bytes).hexdigest())
        self.assertEqual(manifest["python_version"], platform.python_version())
        self.assertEqual(
            manifest["package_versions"],
            {
                "pandas": version("pandas"),
                "numpy": version("numpy"),
                "scikit-learn": version("scikit-learn"),
                "scipy": version("scipy"),
                "joblib": version("joblib"),
            },
        )
        self.assertEqual(
            manifest["split"],
            {
                "test_size": 0.20,
                "test_seed": 23,
                "validation_size_of_dev": 0.25,
                "validation_seed": 24,
            },
        )
        self.assertEqual(
            manifest["student_counts"], {"dev": 4, "train": 3, "validation": 1, "test": 2}
        )
