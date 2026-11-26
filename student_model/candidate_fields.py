from .modeling.estimators import make_ridge
from .modeling.evaluation import errors


def _validation_mae(run, columns):
    train = run["train"]
    validation = run["validation"]
    target = run["schema"]["target"]
    model = make_ridge(columns).fit(train[columns], train[target])
    return errors(validation[target], model.predict(validation[columns]))["mae"]


def assignment_gain(run) -> float:
    """Return the validation MAE reduction in marks from adding assignment completion."""
    columns = run["schema"]["score_features"]
    candidate = [*columns, "assignment_completion_rate"]
    return _validation_mae(run, columns) - _validation_mae(run, candidate)


def revision_gain(run) -> float:
    """Return the validation MAE reduction in marks from adding revision frequency."""
    columns = run["schema"]["score_features"]
    return _validation_mae(run, columns) - _validation_mae(run, [*columns, "revision_frequency"])
