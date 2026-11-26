"""Request and response schemas for desktop study check-ins."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


Percentage = Annotated[float, Field(ge=0, le=100)]
Goal = Literal["remember_material", "finish_coursework"]
Outcome = Literal["helped", "did_not_help", "not_tried"]
StudyMethod = Literal["Flashcards", "Group Study", "Practice Tests", "Self-Reading", "Summarizing"]


class LastCheckIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    goal: Goal | None = None
    outcome: Outcome


class CheckIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    previous_exam_score: Percentage | None = None
    attendance_percentage: Percentage | None = None
    study_hours_per_day: Annotated[float, Field(ge=0, le=24)] | None = None
    practice_tests_completed: Annotated[int, Field(ge=0)] | None = None
    exam_preparation_days: int | None = Field(
        default=None, ge=0, description="Number of days already spent preparing for this exam."
    )
    exam_difficulty: Literal["Easy", "Medium", "Hard"] | None = None
    exam_difficulty_known_before_exam: bool = Field(
        default=False, description="True only for a course rating available at the pre-exam check-in."
    )
    revision_frequency: Literal["Rarely", "Weekly", "Daily"] | None = None
    study_method: StudyMethod | None = None
    assignment_completion_rate: Percentage | None = None
    goal: Goal | None = None
    last_check_in: LastCheckIn | None = None

    @property
    def coaching_goal(self) -> Goal | None:
        return self.goal or (self.last_check_in.goal if self.last_check_in else None)

    @property
    def previous_outcome(self) -> Outcome | None:
        last = self.last_check_in
        if last and (last.goal is None or last.goal == self.coaching_goal):
            return last.outcome
        return None


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    action: str
    follow_up: str


class StudyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_exam_score: Percentage | None
    model_version: str | None
    recommendation: Recommendation
    optional_question: str | None
