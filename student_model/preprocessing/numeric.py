import numpy as np
import pandas as pd


def numeric_column(
    values: pd.Series, lo: float, hi: float | None = None, whole: bool = False
) -> pd.Series:
    """Parse and validate a CSV numeric column in its original units."""
    missing = values.isin(["", "NULL"])
    try:
        numbers = pd.to_numeric(values.mask(missing, np.nan), errors="raise")
    except (TypeError, ValueError) as error:
        raise ValueError(f"{values.name}: {error}") from error

    observed = numbers.dropna()
    if not np.isfinite(observed).all():
        raise ValueError(f"{values.name}: expected finite numbers")
    if (observed < lo).any():
        raise ValueError(f"{values.name}: expected values greater than or equal to {lo}")
    if hi is not None and (observed > hi).any():
        raise ValueError(f"{values.name}: expected values less than or equal to {hi}")
    if whole and (observed % 1 != 0).any():
        raise ValueError(f"{values.name}: expected whole numbers")

    return numbers.astype("float64")
