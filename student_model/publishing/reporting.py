import json
from pathlib import Path


def write_metrics(directory, receipt, test_metrics, slices) -> None:
    """Write the evaluation measurements and suitability decision."""
    document = {
        "validation": receipt,
        "test": test_metrics,
        "slices": slices,
        "suitability": "synthetic_demo_only",
    }
    encoded = json.dumps(document, allow_nan=False, indent=2)
    (Path(directory) / "metrics.json").write_text(encoded + "\n", encoding="utf-8")
