import csv
from os import PathLike

import pandas as pd

from .numeric import numeric_column


HEADER = (
    "student_id",
    "age",
    "gender",
    "education_level",
    "school_type",
    "family_income",
    "parent_education",
    "urban_rural",
    "previous_exam_score",
    "previous_gpa",
    "attendance_percentage",
    "assignment_completion_rate",
    "class_participation",
    "study_hours_per_day",
    "self_study_hours",
    "private_tuition",
    "online_learning_hours",
    "study_consistency",
    "study_environment",
    "study_method",
    "revision_frequency",
    "practice_tests_completed",
    "notes_quality",
    "sleep_hours",
    "sleep_quality",
    "daily_screen_time",
    "physical_activity_hours",
    "break_frequency",
    "stress_level",
    "motivation_level",
    "internet_access",
    "device_availability",
    "educational_app_usage",
    "online_course_hours",
    "exam_difficulty",
    "exam_preparation_days",
    "questions_attempted",
    "questions_correct",
    "time_management_score",
    "exam_anxiety_level",
    "exam_score",
    "performance_grade",
    "pass_status",
    "performance_level",
)

NUMERIC_RULES = (
    (
        100, False,
        (
            "previous_exam_score",
            "attendance_percentage",
            "assignment_completion_rate",
            "time_management_score",
            "exam_score",
        ),
    ),
    (
        24, False,
        (
            "study_hours_per_day",
            "self_study_hours",
            "online_learning_hours",
            "sleep_hours",
            "daily_screen_time",
            "physical_activity_hours",
        ),
    ),
    (
        None, True,
        (
            "age",
            "practice_tests_completed",
            "exam_preparation_days",
            "questions_attempted",
            "questions_correct",
            "stress_level",
        ),
    ),
    (1, True, ("private_tuition", "internet_access")),
    (None, False, ("previous_gpa", "online_course_hours", "exam_anxiety_level")),
)


def read_raw(path: str | PathLike[str]) -> pd.DataFrame:
    """Validate the CSV structure and return its cells as strings."""
    rows = []
    with open(path, encoding="utf-8", newline="") as source:
        reader = csv.reader(source, strict=True)
        try:
            header = next(reader, None)
            if header is None:
                raise ValueError("CSV header is missing")
            if tuple(header) != HEADER:
                raise ValueError("CSV header does not match the expected column order")

            for row in reader:
                if len(row) != len(HEADER):
                    raise ValueError(
                        f"CSV line {reader.line_num}: expected {len(HEADER)} cells, "
                        f"found {len(row)}"
                    )
                rows.append(row)
        except csv.Error as error:
            raise ValueError(f"CSV line {reader.line_num}: {error}") from error

    return pd.DataFrame(rows, columns=HEADER)


def normalize(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a normalized copy with missing tokens and validated numeric values."""
    normalized = dict(raw.mask(raw.isin(["", "NULL"])).items())
    for upper_bound, whole, columns in NUMERIC_RULES:
        for column in columns:
            normalized[column] = numeric_column(
                normalized[column], lo=0, hi=upper_bound, whole=whole
            )
    return pd.DataFrame(normalized, index=raw.index, columns=raw.columns)


def eligible(frame: pd.DataFrame, group_key: str, target: str) -> pd.DataFrame:
    """Validate group IDs and row uniqueness, then keep observed targets."""
    if group_key not in frame.columns:
        raise ValueError(f"Missing group key column: {group_key}")

    groups = frame[group_key]
    if groups.isna().any() or groups.astype("string").str.strip().eq("").any():
        raise ValueError(f"{group_key}: group IDs must be present and nonblank")
    if frame.duplicated().any():
        raise ValueError("Duplicate rows are not allowed")

    observed = frame.loc[frame[target].notna()]
    if observed.empty:
        raise ValueError(f"{target}: no eligible rows with an observed target")
    return observed
