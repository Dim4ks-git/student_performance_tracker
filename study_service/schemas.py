"""Validation for raw desktop study check-ins."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


Percentage = Annotated[float, Field(ge=0, le=100)]


class CheckIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    previous_exam_score: Percentage | None = None
    attendance_percentage: Percentage | None = None
    study_hours_per_day: Annotated[float, Field(ge=0, le=24)] | None = None
    practice_tests_completed: Annotated[int, Field(ge=0)] | None = None
    revision_frequency: Literal["Rarely", "Weekly", "Daily"] | None = None
    assignment_completion_rate: Percentage | None = None
    goal: Literal["remember_material", "finish_coursework"] | None = None
