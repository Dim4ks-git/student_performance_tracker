import unittest

from study_service.advice import tip_key


class TipKeyTests(unittest.TestCase):
    def test_rare_revision_uses_observed_practice_count(self):
        for count, expected in ((0, "make_quiz"), (1, "use_one_test"),
                                (2, "review_mistakes"), (8, "review_mistakes")):
            with self.subTest(count=count):
                self.assertEqual(tip_key("Rarely", count, None), expected)

    def test_other_habits_receive_general_advice(self):
        for frequency, count in (
            ("Rarely", None),
            ("Rarely", -1),
            ("Weekly", 1),
            ("Daily", 0),
            (None, 8),
            (None, None),
        ):
            with self.subTest(frequency=frequency, count=count):
                self.assertEqual(tip_key(frequency, count, None), "general")

    def test_explicit_goals_take_priority(self):
        self.assertEqual(tip_key("Rarely", 1, "finish_coursework"), "coursework")
        self.assertEqual(tip_key("Rarely", 0, "remember_material"), "recall")
        self.assertEqual(tip_key(None, None, "remember_material"), "recall")

    def test_unrecognized_goal_uses_observed_habits(self):
        self.assertEqual(tip_key("Rarely", 1, "other"), "use_one_test")
