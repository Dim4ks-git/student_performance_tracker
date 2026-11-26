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

    async def test_empty_check_in_invites_student_to_choose_goal(self):
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
                "optional_question": "Would you like help remembering material or finishing coursework?",
            },
        )
        self.predictor.predict.assert_not_called()

    async def test_return_visits_use_the_students_goal_and_outcome(self):
        actions = set()
        for goal in ("finish_coursework", "remember_material"):
            first = await self.client.post("/v1/study-check-ins", json={"goal": goal})
            first_action = first.json()["recommendation"]["action"]
            for outcome in ("helped", "did_not_help", "not_tried"):
                prior = {"goal": goal, "outcome": outcome}
                visit = await self.client.post("/v1/study-check-ins", json={"last_check_in": prior})
                self.assertEqual(visit.status_code, 200)
                result = visit.json()
                self.assertIsNone(result["estimated_exam_score"])
                self.assertIsNone(result["optional_question"])
                self.assertNotEqual(result["recommendation"]["action"], first_action)
                actions.add(result["recommendation"]["action"])
            changed = await self.client.post("/v1/study-check-ins", json={
                "goal": goal, "last_check_in": {
                    "goal": "finish_coursework" if goal == "remember_material" else "remember_material",
                    "outcome": "helped",
                },
            })
            self.assertEqual(changed.json(), first.json())
        self.assertEqual(len(actions), 6)

    async def test_unrecognized_outcome_is_rejected(self):
        response = await self.client.post("/v1/study-check-ins", json={
            "last_check_in": {"outcome": "something else"},
        })
        self.assertEqual(response.status_code, 422)

    async def test_401_digit_practice_test_count_returns_advice_without_score(self):
        response = await self.client.post(
            "/v1/study-check-ins",
            json={
                "previous_exam_score": 73.4,
                "study_hours_per_day": 3.42,
                "practice_tests_completed": 10**400,
                "revision_frequency": "Rarely",
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIsNone(result["estimated_exam_score"])
        self.assertIsNone(result["model_version"])
        self.assertIn("several completed tests", result["recommendation"]["reason"])

    async def test_negative_practice_test_count_returns_validation_error(self):
        response = await self.client.post(
            "/v1/study-check-ins", json={"practice_tests_completed": -1}
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"][0]["loc"], ["body", "practice_tests_completed"]
        )
        self.predictor.predict.assert_not_called()

    async def test_nonfinite_numbers_return_field_validation_errors(self):
        for literal in ("NaN", "Infinity", "-Infinity", "1e309"):
            with self.subTest(literal=literal):
                response = await self.client.post(
                    "/v1/study-check-ins",
                    content=f'{{"previous_exam_score": {literal}}}',
                    headers={"Content-Type": "application/json"},
                )
                self.assertEqual(response.status_code, 422)
                error = response.json()["detail"][0]
                self.assertEqual(error["loc"], ["body", "previous_exam_score"])
                self.assertIsInstance(error["input"], str)
        self.predictor.predict.assert_not_called()
