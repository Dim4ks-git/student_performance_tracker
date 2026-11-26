from sklearn.inspection import permutation_importance

from .modeling.estimators import fit_models


def question_value(run) -> dict[str, float]:
    """Return the mean validation MAE increase in marks for each shuffled input."""
    schema = run["schema"]
    columns, estimator = fit_models(run["train"], schema)["score_model"]
    validation = run["validation"]
    result = permutation_importance(
        estimator,
        validation[columns],
        validation[schema["target"]],
        scoring="neg_mean_absolute_error",
        n_repeats=5,
        random_state=23,
    )
    return {
        column: float(increase)
        for column, increase in zip(columns, result.importances_mean, strict=True)
    }
