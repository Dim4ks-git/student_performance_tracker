import unittest
from itertools import combinations

import pandas as pd

from student_model.splits import split_rows


class SplitRowsTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame(
            {
                "student_id": [f"s{student:02d}" for student in range(20)] * 2,
                "exam_score": range(40, 80),
            },
            index=range(101, 141),
        )

    def test_student_counts_and_disjoint_partitions(self):
        dev, train, validation, test = split_rows(self.frame, "student_id")
        partitions = (dev, train, validation, test)
        student_sets = [set(partition["student_id"]) for partition in partitions]
        self.assertEqual([len(ids) for ids in student_sets], [16, 12, 4, 4])
        for left, right in combinations(student_sets[1:], 2):
            self.assertTrue(left.isdisjoint(right))

        self.assertCountEqual(train.index.append(validation.index), dev.index)
        self.assertCountEqual(dev.index.append(test.index), self.frame.index)
        for partition in partitions:
            pd.testing.assert_frame_equal(partition, self.frame.loc[partition.index])

    def test_repeat_call_returns_same_indexes(self):
        first = split_rows(self.frame, "student_id")
        second = split_rows(self.frame, "student_id")
        for first_partition, second_partition in zip(first, second, strict=True):
            pd.testing.assert_index_equal(first_partition.index, second_partition.index)
