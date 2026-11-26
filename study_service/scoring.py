import hashlib
import json
import math
from pathlib import Path

import joblib
import pandas as pd


def load_bundle(directory):
    """Load the score pipeline and ordered features from a trusted local bundle."""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    model_version = manifest["model_version"]
    schema = json.loads((directory / "feature_schema.json").read_text(encoding="utf-8"))
    ordered_features = schema["score_features"]

    with (directory / "score_pipeline.joblib").open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != model_version:
            raise ValueError("score_pipeline.joblib SHA-256 does not match manifest model_version")
        stream.seek(0)
        pipeline = joblib.load(stream)

    return pipeline, ordered_features, model_version


def estimate(answers, bundle) -> tuple[float | None, str | None]:
    """Return a display score and model version for a supported check-in."""
    if (
        bundle is None
        or answers.previous_exam_score is None
        or answers.study_hours_per_day is None
        or answers.practice_tests_completed is None
    ):
        return None, None

    pipeline, ordered_features, model_version = bundle
    attendance = answers.attendance_percentage
    row = {
        "previous_exam_score": answers.previous_exam_score,
        "attendance_percentage": attendance if attendance is not None else math.nan,
        "study_hours_per_day": answers.study_hours_per_day,
        "practice_tests_completed": answers.practice_tests_completed,
    }
    frame = pd.DataFrame([row], columns=ordered_features)

    try:
        score = float(pipeline.predict(frame)[0])
    except ValueError:
        return None, None

    if not math.isfinite(score):
        return None, None
    return min(max(score, 0.0), 100.0), model_version
