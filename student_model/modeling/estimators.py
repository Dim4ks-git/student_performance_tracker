from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def make_ridge() -> Pipeline:
    """Build a fresh Ridge pipeline for a DataFrame in feature order."""
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("ridge", Ridge(alpha=1.0)),
        ]
    )


def fit_models(rows, schema) -> dict:
    """Fit the median and prior-mark baselines and the four-feature Ridge model."""
    target = rows[schema["target"]]
    models = {
        "median": (["previous_exam_score"], DummyRegressor(strategy="median")),
        "previous": (["previous_exam_score"], make_ridge()),
        "ridge4": (list(schema["score_features"]), make_ridge()),
    }
    for columns, estimator in models.values():
        estimator.fit(rows[columns], target)

    return models
