import argparse
import json

from .modeling.estimators import fit_models
from .modeling.evaluation import compare
from .preprocessing.experiment import load_input


def validation_report(run) -> dict:
    """Fit on training students and decide whether the model passes validation."""
    schema = run["schema"]
    models = fit_models(run["train"], schema)
    metrics, _ = compare(models, run["validation"], schema["target"])
    baseline_mae = min(metrics["median"]["mae"], metrics["previous"]["mae"])
    gain_mae = baseline_mae - metrics["score_model"]["mae"]
    return {
        "dataset_sha256": run["dataset_sha256"],
        "score_features": schema["score_features"],
        "metrics": metrics,
        "gain_mae": gain_mae,
        "approved": gain_mae >= 1.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the student score model.")
    parser.add_argument("csv_path", help="Path to the input CSV")
    args = parser.parse_args()
    print(json.dumps(validation_report(load_input(args.csv_path))))


if __name__ == "__main__":
    main()
