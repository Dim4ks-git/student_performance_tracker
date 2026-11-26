from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ..preprocessing.csv_input import DIFFICULTIES


def make_ridge(columns=()) -> Pipeline:
    """Build a fresh Ridge pipeline for a DataFrame in feature order."""
    numeric_steps = [
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]
    levels = {
        "exam_difficulty": DIFFICULTIES,
        "revision_frequency": ("Rarely", "Weekly", "Daily"),
    }
    categorical = [column for column in columns if column in levels]
    if categorical:
        numeric = [column for column in columns if column not in levels]
        encoder = OneHotEncoder(
            categories=[list(levels[column]) for column in categorical],
            handle_unknown="ignore",
            sparse_output=False,
        )
        preprocess = ColumnTransformer([
            ("numeric", Pipeline(numeric_steps), numeric),
            ("categorical", encoder, categorical),
        ])
        return Pipeline([("preprocess", preprocess), ("ridge", Ridge(alpha=1.0))])
    return Pipeline([*numeric_steps, ("ridge", Ridge(alpha=1.0))])


def fit_models(rows, schema) -> dict:
    """Fit the baselines and the schema's pre-exam score model on the same students."""
    target = rows[schema["target"]]
    features = list(schema["score_features"])
    original_four = [
        "previous_exam_score",
        "attendance_percentage",
        "study_hours_per_day",
        "practice_tests_completed",
    ]
    models = {
        "median": (["previous_exam_score"], DummyRegressor(strategy="median")),
        "previous": (["previous_exam_score"], make_ridge()),
        "ridge4": (original_four, make_ridge()),
        "score_model": (features, make_ridge(features)),
    }
    for columns, estimator in models.values():
        estimator.fit(rows[columns], target)

    return models
