import unittest
from waypoint_based_destructible_terrain import *


class TestStringMethods(unittest.TestCase):
    def test_weightless_breadth_first_search(self):
        graph = {}
        self.assertEqual(weightless_breadth_first_search(graph, 0, 0), [])

        graph = {"0": [1], "1": []}
        self.assertEqual(weightless_breadth_first_search(graph, 0, 1), [0, 1])

        graph = {"0": [1], "1": []}
        self.assertEqual(weightless_breadth_first_search(graph, 1, 0), [])


if __name__ == "__main__":
    unittest.main()
