import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


def split_rows(
    frame: pd.DataFrame, group_key: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return development, training, validation, and test rows grouped by student."""
    test_splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=23)
    dev_positions, test_positions = next(test_splitter.split(frame, groups=frame[group_key]))
    dev = frame.iloc[dev_positions]
    test = frame.iloc[test_positions]

    validation_splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=24)
    train_positions, validation_positions = next(
        validation_splitter.split(dev, groups=dev[group_key])
    )
    return dev, dev.iloc[train_positions], dev.iloc[validation_positions], test
