import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


def errors(y, predicted) -> dict[str, float]:
    """Measure prediction error in the original score units."""
    return {
        "mae": float(mean_absolute_error(y, predicted)),
        "rmse": float(root_mean_squared_error(y, predicted)),
    }


def compare(models, rows, target) -> tuple[dict[str, dict[str, float]], pd.Series]:
    """Score each fitted model on the same rows and retain the Ridge predictions."""
    observed = rows[target]
    metrics = {}
    predictions = {}
    for name, (columns, estimator) in models.items():
        predicted = estimator.predict(rows[columns])
        metrics[name] = errors(observed, predicted)
        predictions[name] = predicted

    return metrics, pd.Series(predictions["score_model"], index=rows.index)


def slice_errors(rows, target, predictions) -> dict:
    """Report score errors by observed attendance and education level."""

    def summarize(subset, minimum_rows):
        n = len(subset)
        if n < minimum_rows:
            return {"n": n, "mae": None, "rmse": None}
        return {"n": n, **errors(subset[target], predictions.loc[subset.index])}

    attendance_present = rows["attendance_percentage"].notna()
    cohorts = rows.groupby("education_level", observed=True, dropna=True)
    return {
        "attendance_present": summarize(rows.loc[attendance_present], 1),
        "attendance_missing": summarize(rows.loc[~attendance_present], 1),
        "education_level": {
            level: summarize(subset, 30) for level, subset in cohorts
        },
    }
