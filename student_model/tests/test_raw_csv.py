import csv
import tempfile
import unittest
from pathlib import Path

from student_model.data import HEADER, read_raw


class ReadRawTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "students.csv"
        self.row = [""] * 44
        self.row[0] = "001"
        self.row[4] = "Public, charter"
        self.row[21] = "0"

    def write_csv(self, *records):
        with self.path.open("w", encoding="utf-8", newline="") as output:
            csv.writer(output).writerows(records)

    def test_preserves_quoted_commas_and_raw_strings(self):
        self.write_csv(HEADER, self.row)

        frame = read_raw(self.path)

        self.assertEqual(tuple(frame.columns), HEADER)
        self.assertEqual(frame.shape, (1, 44))
        self.assertEqual(frame.iloc[0].tolist(), self.row)
        self.assertEqual(frame.at[0, "school_type"], "Public, charter")
        self.assertEqual(frame.at[0, "attendance_percentage"], "")

    def test_rejects_empty_file(self):
        self.path.touch()

        with self.assertRaisesRegex(ValueError, "header"):
            read_raw(self.path)

    def test_rejects_reordered_header(self):
        header = list(HEADER)
        header[0], header[1] = header[1], header[0]
        self.write_csv(header, self.row)

        with self.assertRaisesRegex(ValueError, "header"):
            read_raw(self.path)

    def test_rejects_short_and_long_records_after_valid_row(self):
        for invalid_row in (self.row[:-1], [*self.row, "extra"]):
            with self.subTest(width=len(invalid_row)):
                self.write_csv(HEADER, self.row, invalid_row)

                with self.assertRaisesRegex(ValueError, "CSV line 3"):
                    read_raw(self.path)

    def test_rejects_unfinished_quote(self):
        self.write_csv(HEADER)
        with self.path.open("a", encoding="utf-8", newline="") as output:
            output.write('"unfinished')

        with self.assertRaisesRegex(ValueError, "CSV line 2"):
            read_raw(self.path)


if __name__ == "__main__":
    unittest.main()
