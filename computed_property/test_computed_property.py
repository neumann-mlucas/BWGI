import unittest
from unittest.mock import patch, MagicMock, call
from computed_property import computed_property


class Rectangle:
    def __init__(self, width=5, height=10):
        self.width = width
        self.height = height
        self.mock_tracker = MagicMock()

    @computed_property("width", "height", "dummy")
    def area(self):
        self.mock_tracker()
        return self.width * self.height

    @area.setter
    def area(self, value):
        ratio = self.width / self.height
        self.width = (value / ratio) ** (1 / 2)
        self.height = (value * ratio) ** (1 / 2)

    @area.deleter
    def area(self):
        self.width = 0
        self.height = 0


class TestComputedProperty(unittest.TestCase):
    def test_method_call_width_update(self):
        # Create a mock that we'll use to count calls
        rect = Rectangle()

        # First access should call the method
        self.assertEqual(rect.area, 50)
        self.assertEqual(rect.mock_tracker.call_count, 1)

        # Second access should use cached value
        self.assertEqual(rect.area, 50)
        self.assertEqual(rect.mock_tracker.call_count, 1)

        rect.width = 8

        # Third access should recalculate
        self.assertEqual(rect.area, 80)
        self.assertEqual(rect.mock_tracker.call_count, 2)

        # Fourth access should use cached value
        self.assertEqual(rect.area, 80)
        self.assertEqual(rect.mock_tracker.call_count, 2)

    def test_method_call_height_update(self):
        # Create a mock that we'll use to count calls
        rect = Rectangle()

        # First access should call the method
        self.assertEqual(rect.area, 50)
        self.assertEqual(rect.mock_tracker.call_count, 1)

        rect.height = 8

        # Third access should recalculate
        self.assertEqual(rect.area, 40)
        self.assertEqual(rect.mock_tracker.call_count, 2)

        # Fourth access should use cached value
        self.assertEqual(rect.area, 40)
        self.assertEqual(rect.mock_tracker.call_count, 2)

    def test_method_setter(self):
        # Create a mock that we'll use to count calls
        rect = Rectangle()

        # First access should call the method
        self.assertEqual(rect.area, 50)
        self.assertEqual(rect.mock_tracker.call_count, 1)

        rect.area = 100

        # Second access should recalculate
        self.assertAlmostEqual(rect.area, 100)
        self.assertEqual(rect.mock_tracker.call_count, 2)

        # Third access should use cached value
        self.assertAlmostEqual(rect.area, 100)
        self.assertEqual(rect.mock_tracker.call_count, 2)

    def test_method_deletter(self):
        # Create a mock that we'll use to count calls
        rect = Rectangle()

        # First access should call the method
        self.assertEqual(rect.area, 50)
        self.assertEqual(rect.mock_tracker.call_count, 1)

        del rect.area

        # Second access should recalculate
        self.assertAlmostEqual(rect.area, 0)
        self.assertEqual(rect.mock_tracker.call_count, 2)

        # Third access should use cached value
        self.assertAlmostEqual(rect.area, 0)
        self.assertEqual(rect.mock_tracker.call_count, 2)


if __name__ == "__main__":
    unittest.main()
