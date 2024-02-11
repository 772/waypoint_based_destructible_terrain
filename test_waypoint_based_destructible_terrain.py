import unittest
from waypoint_based_destructible_terrain import *


class Test(unittest.TestCase):
    def test_weightless_breadth_first_search(self):
        graph = {}
        self.assertEqual(weightless_breadth_first_search(graph, 0, 0), [])

        graph = {"0": [1], "1": [2], "2": []}
        self.assertEqual(weightless_breadth_first_search(graph, 0, 2), [0, 1, 2])
        self.assertEqual(weightless_breadth_first_search(graph, 2, 0), [])

    def test_humanplayer_init(self):
        human = HumanPlayer(10, 20, (1, 2, 3))
        self.assertEqual(human.x_position, 10)
        self.assertEqual(human.y_position, 20)
        self.assertEqual(human.color, (1, 2, 3))

    def test_aiplayer_init(self):
        ai = AIPlayer(10, 20, (1, 2, 3))
        self.assertEqual(ai.x_position, 10)
        self.assertEqual(ai.y_position, 20)
        self.assertEqual(ai.color, (1, 2, 3))

    def test_game_state_init(self):
        game_state = GameState()
        self.assertEqual(len(game_state.flags), 6)
        self.assertEqual(len(game_state.tunnels), 11)

    def test_game_state_draw(self):
        game_state = GameState()
        game_state.draw()
        self.assertEqual(
            game_state.players[0].is_there_solid_material(game_state.screen, 0, 0),
            False,
        )
        self.assertEqual(
            game_state.players[0].is_there_solid_material(game_state.screen, 0, 10),
            True,
        )


if __name__ == "__main__":
    unittest.main()
