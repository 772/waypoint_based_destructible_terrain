import unittest
from waypoint_based_destructible_terrain import *


class Test(unittest.TestCase):
    def test_weightless_breadth_first_search(self):
        graph = {}
        self.assertEqual(weightless_breadth_first_search(graph, 0, 0), [])

        graph = {"0": [1], "1": [2], "2": []}
        self.assertEqual(weightless_breadth_first_search(graph, 0, 2), [0, 1, 2])
        self.assertEqual(weightless_breadth_first_search(graph, 2, 0), [])

    def test_humanplayer(self):
        human = HumanPlayer(500, 300, (255, 100, 0))
        self.assertEqual(human.color, (255, 100, 0))

    def test_aiplayer(self):
        ai = AIPlayer(700, 500, (255, 0, 0))
        self.assertEqual(ai.color, (255, 0, 0))


if __name__ == "__main__":
    unittest.main()
