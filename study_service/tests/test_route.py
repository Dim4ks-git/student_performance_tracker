import unittest
from unittest.mock import Mock

import httpx

from study_service.api import create_app


class StudyCheckInRouteTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.predictor = Mock()
        self.predictor.predict.return_value = [71.9617451655]
        features = [
            "previous_exam_score",
            "attendance_percentage",
            "study_hours_per_day",
            "practice_tests_completed",
        ]
        bundle = (self.predictor, features, "v1")
        app = create_app(bundle)
        self.client = await self.enterAsyncContext(
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            )
        )

    async def test_complete_check_in_returns_estimate_and_quiz_action(self):
        response = await self.client.post(
            "/v1/study-check-ins",
            json={
                "previous_exam_score": 73.4,
                "attendance_percentage": None,
                "study_hours_per_day": 3.42,
                "practice_tests_completed": 0,
                "revision_frequency": "Rarely",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "estimated_exam_score": 71.9617451655,
                "model_version": "v1",
                "recommendation": {
                    "reason": "You reported infrequent revision and zero completed practice tests.",
                    "action": "Make a five-question quiz from your class notes and try it from memory.",
                    "follow_up": "Can you answer the missed questions on another day?",
                },
                "optional_question": None,
            },
        )
        self.predictor.predict.assert_called_once()

    async def test_empty_check_in_returns_general_action_and_previous_mark_question(self):
        response = await self.client.post("/v1/study-check-ins", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "estimated_exam_score": None,
                "model_version": None,
                "recommendation": {
                    "reason": "A short practice session can give you a starting point.",
                    "action": "Pick one topic and try recalling it before checking your notes.",
                    "follow_up": "Which part would you like help with next?",
                },
                "optional_question": "What was your last comparable exam mark out of 100?",
            },
        )
        self.predictor.predict.assert_not_called()

    async def test_negative_practice_test_count_returns_validation_error(self):
        response = await self.client.post(
            "/v1/study-check-ins", json={"practice_tests_completed": -1}
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"][0]["loc"], ["body", "practice_tests_completed"]
        )
        self.predictor.predict.assert_not_called()
