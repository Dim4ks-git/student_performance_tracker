import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from student_model.data import HEADER
from student_model.experiment import load_input


class LoadInputTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "students.csv"
        with self.path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(HEADER)
            for student in range(20):
                writer.writerow(self.make_row(f"s{student:02d}", 50))

    @staticmethod
    def make_row(student_id, target):
        row = [""] * len(HEADER)
        row[HEADER.index("student_id")] = student_id
        row[HEADER.index("exam_score")] = target
        return row

    def assert_partitions(self, run):
        partitions = {"dev": 16, "train": 12, "validation": 4, "test": 4}
        for name, count in partitions.items():
            with self.subTest(partition=name):
                self.assertEqual(run[name]["student_id"].nunique(), count)
                self.assertTrue(run[name]["exam_score"].eq(50).all())

    def test_loads_schema_digest_and_partitions(self):
        run = load_input(self.path)

        self.assertEqual(set(run), {"schema", "dataset_sha256", "dev", "train", "validation", "test"})
        self.assertEqual(
            run["schema"],
            {
                "score_features": [
                    "previous_exam_score",
                    "attendance_percentage",
                    "study_hours_per_day",
                    "practice_tests_completed",
                ],
                "target": "exam_score",
                "group_key": "student_id",
            },
        )
        self.assertEqual(run["dataset_sha256"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assert_partitions(run)

    def test_unobserved_target_changes_digest_but_keeps_partition_counts(self):
        before = load_input(self.path)
        with self.path.open("a", encoding="utf-8", newline="") as stream:
            csv.writer(stream).writerow(self.make_row("s20", ""))

        after = load_input(self.path)

        self.assertEqual(after["dataset_sha256"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertNotEqual(before["dataset_sha256"], after["dataset_sha256"])
        self.assert_partitions(after)
