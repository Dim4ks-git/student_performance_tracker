import os
import unittest
from unittest.mock import Mock, patch

import httpx

from study_service.server import app


class StudyServiceStartupTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = await self.enterAsyncContext(
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            )
        )
        self.answers = {
            "previous_exam_score": 73.4,
            "study_hours_per_day": 3.42,
            "practice_tests_completed": 0,
            "revision_frequency": "Rarely",
        }

    async def check_in(self):
        response = await self.client.post("/v1/study-check-ins", json=self.answers)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result["recommendation"]["action"])
        return result

    @patch.dict(os.environ, {"STUDY_MODEL_DIR": "test-bundle"})
    @patch("study_service.server.load_bundle")
    async def test_loads_once_for_two_scored_check_ins(self, load_bundle):
        predictor = Mock()
        predictor.predict.return_value = [72.0]
        load_bundle.return_value = (
            predictor,
            [
                "previous_exam_score",
                "attendance_percentage",
                "study_hours_per_day",
                "practice_tests_completed",
            ],
            "v1",
        )

        load_bundle.assert_not_called()
        async with app.router.lifespan_context(app):
            for _ in range(2):
                result = await self.check_in()
                self.assertEqual(result["estimated_exam_score"], 72.0)
                self.assertEqual(result["model_version"], "v1")
        load_bundle.assert_called_once_with("test-bundle")

    @patch.dict(os.environ, {"STUDY_MODEL_DIR": "test-bundle"})
    @patch("study_service.server.load_bundle", side_effect=ValueError("Invalid bundle"))
    async def test_failed_load_still_serves_advice(self, load_bundle):
        with self.assertLogs("study_service.server", level="WARNING"):
            async with app.router.lifespan_context(app):
                result = await self.check_in()
                self.assertIsNone(result["estimated_exam_score"])
                self.assertIsNone(result["model_version"])
        load_bundle.assert_called_once_with("test-bundle")

    @patch.dict(os.environ)
    @patch("study_service.server.load_bundle")
    async def test_unset_model_directory_serves_advice_without_loading(self, load_bundle):
        os.environ.pop("STUDY_MODEL_DIR", None)
        async with app.router.lifespan_context(app):
            result = await self.check_in()
            self.assertIsNone(result["estimated_exam_score"])
            self.assertIsNone(result["model_version"])
        load_bundle.assert_not_called()
