import unittest
import tempfile

import last_lines


def write_temp_file(lines):
    tf = tempfile.NamedTemporaryFile(delete=False, mode="wb")
    tf.write(lines)
    tf.close()
    return tf.name


class TestLastLines(unittest.TestCase):
    def test_simple_reverse(self):
        lines = b"first\nsecond\nthird"
        file_name = write_temp_file(lines)
        with open(file_name, "rb") as file:
            reversed_lines = last_lines.last_lines(file)
            self.assertEqual(next(reversed_lines), b"third")
            self.assertEqual(next(reversed_lines), b"second\n")
            self.assertEqual(next(reversed_lines), b"first\n")

    def test_buffsize(self):
        lines = b"first\nsecond\nlong long long line"
        file_name = write_temp_file(lines)
        with open(file_name, "rb") as file:
            reversed_lines = last_lines.last_lines(file, bufsize=10)
            self.assertEqual(next(reversed_lines), b"long line")
            self.assertEqual(next(reversed_lines), b"long long ")
            self.assertEqual(next(reversed_lines), b"second\n")
            self.assertEqual(next(reversed_lines), b"first\n")


class TestLastLinesUnicode(unittest.TestCase):
    def test_trumcated_utf8(self):
        lines = b"Caf\xc3\nCaf\xc3\xa9"
        file_name = write_temp_file(lines)

        with open(file_name, "rb") as file:
            reversed_lines = map(
                last_lines.clean_bytes, last_lines.last_lines(file, bufsize=10)
            )
            self.assertEqual(next(reversed_lines), "Café")
            self.assertEqual(next(reversed_lines), "Caf�\n")

    def test_buffsize_trumcated_utf8(self):
        lines = b"Caf\xc3\xa9"
        file_name = write_temp_file(lines)

        with open(file_name, "rb") as file:
            reversed_lines = map(
                last_lines.clean_bytes, last_lines.last_lines(file, bufsize=2)
            )
            self.assertEqual(next(reversed_lines), "�")
            self.assertEqual(next(reversed_lines), "f�")
            self.assertEqual(next(reversed_lines), "Ca")


if __name__ == "__main__":
    unittest.main()
