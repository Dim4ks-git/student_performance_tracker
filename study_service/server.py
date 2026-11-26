"""Uvicorn entry point for the local study service."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from study_service.api import create_app
from study_service.scoring import load_bundle

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    directory = os.environ.get("STUDY_MODEL_DIR")
    bundle = None
    if directory:
        try:
            bundle = load_bundle(directory)
        except Exception:
            logger.warning(
                "Could not load the study model bundle. Serving advice only.",
                exc_info=True,
            )
    app.state.bundle = bundle
    yield


app = create_app(lifespan=lifespan)
