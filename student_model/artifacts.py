import hashlib
import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

import joblib
import pandas as pd


_PINNED_DATASET_SHA256 = "3967020b770568f9a732387f04907807bf0c39cd1d8c96077e36646387cdf1bc"
_PINNED_PREDICTION = 71.9617451655
_ATOL = 1e-6


def save_model(directory, pipeline, schema, dataset_sha256) -> None:
    """Save a fitted pipeline in a staging directory and verify its reference prediction."""
    directory = Path(directory)
    reference_input = [73.4, None, 3.42, 10]
    frame = pd.DataFrame([reference_input], columns=schema["score_features"], dtype=float)
    expected = float(pipeline.predict(frame)[0])
    pipeline_path = directory / "score_pipeline.joblib"
    joblib.dump(pipeline, pipeline_path)
    (directory / "feature_schema.json").write_text(
        json.dumps(schema, allow_nan=False), encoding="utf-8"
    )

    actual = float(joblib.load(pipeline_path).predict(frame)[0])
    if not math.isfinite(expected) or not math.isclose(
        actual, expected, rel_tol=0, abs_tol=_ATOL
    ):
        raise ValueError("Reloaded prediction differs from the pre-save reference.")
    if dataset_sha256 == _PINNED_DATASET_SHA256 and not math.isclose(
        actual, _PINNED_PREDICTION, rel_tol=0, abs_tol=_ATOL
    ):
        raise ValueError("Reloaded prediction differs from the published reference.")

    reference = {"input": reference_input, "expected": expected, "atol": _ATOL}
    (directory / "reference.json").write_text(
        json.dumps(reference, allow_nan=False), encoding="utf-8"
    )


def write_manifest(directory, run) -> None:
    """Record the staged model's identity and the training run configuration."""
    directory = Path(directory)
    with (directory / "score_pipeline.joblib").open("rb") as stream:
        model_version = hashlib.file_digest(stream, "sha256").hexdigest()

    group_key = run["schema"]["group_key"]
    manifest = {
        "dataset_sha256": run["dataset_sha256"],
        "model_version": model_version,
        "python_version": platform.python_version(),
        "package_versions": {
            name: version(name)
            for name in ("pandas", "numpy", "scikit-learn", "scipy", "joblib")
        },
        "split": {
            "test_size": 0.20,
            "test_seed": 23,
            "validation_size_of_dev": 0.25,
            "validation_seed": 24,
        },
        "student_counts": {
            name: run[name][group_key].nunique()
            for name in ("dev", "train", "validation", "test")
        },
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, allow_nan=False), encoding="utf-8"
    )
