"""HTTP API for local study check-ins."""

from fastapi import FastAPI, Request

from study_service.advice import next_question, recommendation
from study_service.schemas import CheckIn, StudyResult
from study_service.scoring import estimate


def create_app(bundle=None, *, lifespan=None) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.state.bundle = bundle

    @app.post("/v1/study-check-ins", response_model=StudyResult)
    def study_check_in(answers: CheckIn, request: Request):
        score, version = estimate(answers, request.app.state.bundle)
        return {
            "estimated_exam_score": score,
            "model_version": version,
            "recommendation": recommendation(answers),
            "optional_question": next_question(answers),
        }

    return app
