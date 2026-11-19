from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .modeling.estimators import fit_models, make_ridge
from .modeling.evaluation import errors


def assignment_gain(run) -> float:
    """Return the validation MAE reduction in marks from adding assignment completion."""
    schema = run["schema"]
    train = run["train"]
    validation = run["validation"]
    target = schema["target"]
    observed = validation[target]

    baseline_columns, baseline = fit_models(train, schema)["ridge4"]
    baseline_mae = errors(observed, baseline.predict(validation[baseline_columns]))["mae"]

    candidate_columns = [*schema["score_features"], "assignment_completion_rate"]
    candidate = make_ridge()
    candidate.fit(train[candidate_columns], train[target])
    candidate_mae = errors(observed, candidate.predict(validation[candidate_columns]))["mae"]

    return baseline_mae - candidate_mae


def revision_gain(run) -> float:
    """Return the validation MAE reduction in marks from adding revision frequency."""
    schema = run["schema"]
    train = run["train"]
    validation = run["validation"]
    target = schema["target"]
    observed = validation[target]

    baseline_columns, baseline = fit_models(train, schema)["ridge4"]
    baseline_mae = errors(observed, baseline.predict(validation[baseline_columns]))["mae"]

    revision_columns = ["revision_frequency"]
    candidate_columns = [*baseline_columns, *revision_columns]
    numeric = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    preprocess = ColumnTransformer(
        [
            ("numeric", numeric, baseline_columns),
            (
                "revision",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                revision_columns,
            ),
        ]
    )
    candidate = Pipeline([("preprocess", preprocess), ("ridge", Ridge(alpha=1.0))])
    candidate.fit(train[candidate_columns], train[target])
    candidate_mae = errors(observed, candidate.predict(validation[candidate_columns]))["mae"]

    return baseline_mae - candidate_mae
