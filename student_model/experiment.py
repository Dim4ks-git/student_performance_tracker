import hashlib
import json
from os import PathLike
from pathlib import Path

from .data import eligible, normalize, read_raw
from .splits import split_rows


def load_input(path: str | PathLike[str]) -> dict:
    """Fingerprint an immutable CSV and prepare its grouped training partitions."""
    with open(path, "rb") as stream:
        dataset_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()

    schema_path = Path(__file__).with_name("feature_schema.json")
    with schema_path.open(encoding="utf-8") as stream:
        schema = json.load(stream)

    group_key = schema["group_key"]
    frame = normalize(read_raw(path))
    rows = eligible(frame, group_key, schema["target"])
    dev, train, validation, test = split_rows(rows, group_key)
    return {
        "schema": schema,
        "dataset_sha256": dataset_sha256,
        "dev": dev,
        "train": train,
        "validation": validation,
        "test": test,
    }
