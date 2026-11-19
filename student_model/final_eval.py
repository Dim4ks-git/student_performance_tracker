from .estimators import fit_models
from .evaluation import compare, slice_errors


def final_evaluation(run, receipt) -> tuple:
    """Refit on development rows and evaluate the holdout after receipt checks."""
    schema = run["schema"]
    if receipt.get("approved") is not True:
        raise ValueError("Final evaluation requires an approved validation receipt.")
    if receipt.get("dataset_sha256") != run["dataset_sha256"]:
        raise ValueError("Validation receipt dataset hash does not match the input.")
    if receipt.get("score_features") != schema["score_features"]:
        raise ValueError("Validation receipt score features do not match the schema order.")

    models = fit_models(run["dev"], schema)
    test_rows = run["test"]
    target = schema["target"]
    final_metrics, predictions = compare(models, test_rows, target)
    slices = slice_errors(test_rows, target, predictions)
    return models["ridge4"][1], final_metrics, slices
