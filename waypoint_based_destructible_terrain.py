"""
Project name: waypoint_based_destructible_terrain
Author: Armin Schäfer
Requirements: ```pip install pygame```
"""

import math
import sys
from player import *
from enum import Enum, auto

# Third-party libraries.
import pygame

# Constants.
FPS: int = 36
WORLD_SIZE = (1920, 1080)
DEFAULT_WINDOW_SIZE = (1200, 820)
EARTH_COLOR = (200, 130, 110)  # Brownish color.
LIGHT_EARTH_COLOR = (220, 150, 130)  # Lighter than EARTH_COLOR.
DARK_EARTH_COLOR = (180, 110, 90)  # Darker than EARTH_COLOR.
TUNNEL_COLOR = (100, 30, 10)  # Should be darker than earth color.
SPEED_WALKING: int = 2  # How fast the player is walking/jumping to left or right.
SPEED_DIGGING: int = 1  # Should be lower than SPEED_WALKING.
SPEED_JUMPING: float = 3.5  # Vertical jumping speed.
BUTTON_DEBUG_X: int = 10
BUTTON_DEBUG_Y: int = 45
BUTTON_DEBUG_WDT: int = 270
BUTTON_DEBUG_HGT: int = 40
BUTTON_RESET_X: int = 300
BUTTON_RESET_Y: int = 45
BUTTON_RESET_WDT: int = 100
BUTTON_RESET_HGT: int = 40
PLAYER_HGT: int = 20  # How tall the player is.
PLAYER_WDT: int = 10  # How wide the player is.
TUNNEL_HGT: int = 40  # The tunnel height should be at least as big as PLAYER_HGT.
DEGREE_45: float = TUNNEL_HGT / 2 * math.sin(math.radians(45))  # Tunnels going down.
DEGREE_22_X: float = TUNNEL_HGT / 2 * math.sin(math.radians(22.5))  # Tunnels going up.
DEGREE_22_Y: float = TUNNEL_HGT / 2 * math.cos(math.radians(22.5))  # Tunnels going up.


class Flag:
    """Visual checkpoint that is only used for decoration."""

    x_position: float
    y_position: float
    color: tuple

    def __init__(self, x_position, y_position, color):
        self.x_position = x_position
        self.y_position = y_position
        self.color = color

    def draw(self, screen):
        """Draws a small flag to screen."""
        pygame.draw.polygon(
            screen,
            self.color,
            (
                (self.x_position, self.y_position),
                (self.x_position, self.y_position - 30),
                (self.x_position + 15, self.y_position - 25),
                (self.x_position + 1, self.y_position - 20),
                (self.x_position + 1, self.y_position),
            ),
            0,
        )


class TunnelDirection(Enum):
    """Used by the class Tunnel. A player can dig to six directions. We need an enum for this
    because we need to draw a tunnel depending on the direction of the tunnel."""

    FLAT = auto()
    RIGHTUP = auto()
    RIGHTDOWN = auto()
    LEFTUP = auto()
    LEFTDOWN = auto()


class Tunnel:
    """A hole in the earth. Players can jump and walk in tunnels."""

    start_x: float
    start_y: float
    end_x: float
    end_y: float
    direction: TunnelDirection

    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.direction = TunnelDirection.FLAT  # Default value.
        if start_y < end_y:
            if start_x < end_x:
                self.direction = TunnelDirection.RIGHTDOWN
            else:
                self.direction = TunnelDirection.LEFTDOWN
        elif start_y > end_y:
            if start_x < end_x:
                self.direction = TunnelDirection.RIGHTUP
            else:
                self.direction = TunnelDirection.LEFTUP

    def draw(self, screen, color, offset):
        """Draws a dark brown tunnel to screen."""
        pygame.draw.circle(
            screen,
            color,
            (self.end_x, self.end_y - TUNNEL_HGT / 2 + offset),
            TUNNEL_HGT / 2,
        )
        if self.start_x == self.end_x:
            return
        self.start_y += offset
        self.end_y += offset
        if self.direction == TunnelDirection.FLAT:
            pygame.draw.polygon(
                screen,
                color,
                (
                    (self.start_x, self.start_y),
                    (self.start_x, self.start_y - TUNNEL_HGT),
                    (self.end_x, self.end_y - TUNNEL_HGT),
                    (self.end_x, self.end_y),
                ),
                0,
            )
        elif self.direction == TunnelDirection.RIGHTUP:
            pygame.draw.polygon(
                screen,
                color,
                (
                    (
                        self.start_x + DEGREE_22_X,
                        self.start_y - TUNNEL_HGT / 2 + DEGREE_22_Y,
                    ),
                    (
                        self.start_x - DEGREE_22_X,
                        self.start_y - TUNNEL_HGT / 2 - DEGREE_22_Y,
                    ),
                    (
                        self.end_x - DEGREE_22_X,
                        self.end_y - TUNNEL_HGT / 2 - DEGREE_22_Y,
                    ),
                    (
                        self.end_x + DEGREE_22_X,
                        self.end_y - TUNNEL_HGT / 2 + DEGREE_22_Y,
                    ),
                ),
                0,
            )
        elif self.direction == TunnelDirection.RIGHTDOWN:
            pygame.draw.polygon(
                screen,
                color,
                (
                    (
                        self.start_x - DEGREE_22_X,
                        self.start_y - TUNNEL_HGT / 2 + DEGREE_22_Y,
                    ),
                    (
                        self.start_x + DEGREE_22_X,
                        self.start_y - TUNNEL_HGT / 2 - DEGREE_22_Y,
                    ),
                    (
                        self.end_x + DEGREE_22_X,
                        self.end_y - TUNNEL_HGT / 2 - DEGREE_22_Y,
                    ),
                    (
                        self.end_x - DEGREE_22_X,
                        self.end_y - TUNNEL_HGT / 2 + DEGREE_22_Y,
                    ),
                ),
                0,
            )
        elif self.direction == TunnelDirection.LEFTUP:
            pygame.draw.polygon(
                screen,
                color,
                (
                    (
                        self.start_x - DEGREE_22_X,
                        self.start_y - TUNNEL_HGT / 2 + DEGREE_22_Y,
                    ),
                    (
                        self.start_x + DEGREE_22_X,
                        self.start_y - TUNNEL_HGT / 2 - DEGREE_22_Y,
                    ),
                    (
                        self.end_x + DEGREE_22_X,
                        self.end_y - TUNNEL_HGT / 2 - DEGREE_22_Y,
                    ),
                    (
                        self.end_x - DEGREE_22_X,
                        self.end_y - TUNNEL_HGT / 2 + DEGREE_22_Y,
                    ),
                ),
                0,
            )
        elif self.direction == TunnelDirection.LEFTDOWN:
            pygame.draw.polygon(
                screen,
                color,
                (
                    (
                        self.start_x + DEGREE_45,
                        self.start_y - TUNNEL_HGT / 2 + DEGREE_45,
                    ),
                    (
                        self.start_x - DEGREE_45,
                        self.start_y - TUNNEL_HGT / 2 - DEGREE_45,
                    ),
                    (
                        self.end_x - DEGREE_45,
                        self.end_y - TUNNEL_HGT / 2 - DEGREE_45,
                    ),
                    (
                        self.end_x + DEGREE_45,
                        self.end_y - TUNNEL_HGT / 2 + DEGREE_45,
                    ),
                ),
                0,
            )
        self.start_y -= offset
        self.end_y -= offset


class GameState:
    """Contains all important infos about the game."""

    screen: pygame.surface.Surface
    clock: pygame.time.Clock
    debug_mode: bool
    font_big: pygame.font.Font
    font_medium: pygame.font.Font
    font_small: pygame.font.Font
    text: pygame.Surface
    text_reset: pygame.surface.Surface
    text_goal: pygame.surface.Surface
    flags = list
    tunnels = list
    players = list
    waypoint_net = dict

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("waypoint based destructible terrain")
        self.screen = pygame.display.set_mode(DEFAULT_WINDOW_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.debug_mode = False
        self.font_big = pygame.font.SysFont("Arial", 26)
        self.font_medium = pygame.font.SysFont("Arial", 19)
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.text = self.font_big.render("Turn on debug mode", True, (0, 0, 0))
        self.text_reset = self.font_big.render("Reset", True, (0, 0, 0))
        self.text_goal = self.font_medium.render(
            "Move via arrow keys. Start/end digging via left or right Control. Dig a tunnel to the red flag to make the AI move between the red flags.",
            True,
            (0, 0, 0),
        )
        # Place flags.
        self.flags = []
        self.flags.append(Flag(100, 300, (255, 0, 0)))  # Red flag.
        self.flags.append(Flag(720, 500, (255, 0, 0)))  # Red flag.
        self.flags.append(Flag(100, 600, (255, 255, 0)))  # Yellow flag.
        self.flags.append(Flag(300, 800, (255, 255, 0)))  # Yellow flag.
        self.flags.append(Flag(300, 600, (0, 255, 0)))  # Green flag.
        self.flags.append(Flag(50, 800, (0, 255, 0)))  # Green flag.
        self.flags.append(Flag(400, 600, (0, 255, 255)))  # Teal flag.
        self.flags.append(Flag(400, 800, (0, 255, 255)))  # Teal flag.
        self.flags.append(Flag(550, 600, (255, 255, 255)))  # White flag.
        self.flags.append(Flag(550, 800, (255, 255, 255)))  # White flag.
        # Place some tunnels connecting the flags. Since the tunnels are placed manually, the
        # waypoint net must be filled manually afterwards. When playing, there is no need for this.
        self.tunnels = []
        # Tunnels for red flags.
        self.tunnels.append(Tunnel(100, 300, 100, 300))  # ID = 0.
        self.tunnels.append(Tunnel(100, 300, 600, 300))  # ID = 1.
        self.tunnels.append(Tunnel(680, 500, 680, 500))  # ID = 2.
        self.tunnels.append(Tunnel(680, 500, 720, 500))  # ID = 3.
        # Tunnels for yellow flags.
        self.tunnels.append(Tunnel(100, 600, 100, 600))  # ID = 4.
        self.tunnels.append(Tunnel(100, 600, 200, 700))  # ID = 5.
        self.tunnels.append(Tunnel(200, 700, 300, 800))  # ID = 6.
        # Tunnels for green flags.
        self.tunnels.append(Tunnel(300, 600, 300, 600))  # ID = 7.
        self.tunnels.append(Tunnel(300, 600, 200, 700))  # ID = 8.
        self.tunnels.append(Tunnel(200, 700, 100, 800))  # ID = 9.
        self.tunnels.append(Tunnel(100, 800, 50, 800))  # ID = 10.
        # Tunnels for teal flags.
        self.tunnels.append(Tunnel(400, 600, 400, 600))  # ID = 11.
        self.tunnels.append(Tunnel(400, 600, 450, 650))  # ID = 12.
        self.tunnels.append(Tunnel(450, 650, 400, 700))  # ID = 13.
        self.tunnels.append(Tunnel(400, 700, 450, 750))  # ID = 14.
        self.tunnels.append(Tunnel(450, 750, 400, 800))  # ID = 15.
        # Tunnels for white flags.
        self.tunnels.append(Tunnel(550, 600, 550, 600))  # ID = 16.
        self.tunnels.append(Tunnel(550, 600, 650, 600))  # ID = 17.
        self.tunnels.append(Tunnel(650, 600, 550, 700))  # ID = 18.
        self.tunnels.append(Tunnel(550, 700, 650, 700))  # ID = 19.
        self.tunnels.append(Tunnel(650, 700, 550, 800))  # ID = 20.
        # The waypoint net that knows which tunnels are connected.
        self.waypoint_net = {
            "0": {1},
            "1": {0},
            "2": {3},
            "3": {2},
            "4": {5},
            "5": {4, 6, 7, 9},
            "6": {5},
            "7": {8},
            "8": {4, 6, 7, 9},
            "9": {8, 10},
            "10": {9},
            "11": {12},
            "12": {11, 13},
            "13": {12, 14},
            "14": {13, 15},
            "15": {14},
            "16": {17},
            "17": {16, 18},
            "18": {17, 19},
            "19": {18, 20},
            "20": {19},
        }
        # Place players.
        self.players = []
        self.players.append(HumanPlayer(300, 300, (255, 100, 0)))  # Human player.
        self.players.append(AIPlayer(700, 500, (255, 0, 0)))  # Patrolling red flags.
        self.players[-1].patrol_between_tunnels = [0, 3]
        self.players[-1].last_visited_tunnels = 3
        self.players.append(AIPlayer(100, 600, (255, 255, 0)))  # Patrolling yel. flags.
        self.players[-1].patrol_between_tunnels = [6, 4]
        self.players[-1].last_visited_tunnels = 4
        self.players.append(AIPlayer(300, 600, (0, 255, 0)))  # Patrolling green flags.
        self.players[-1].patrol_between_tunnels = [10, 7]
        self.players[-1].last_visited_tunnels = 7
        self.players.append(AIPlayer(400, 600, (0, 255, 255)))  # Patrolling teal flags.
        self.players[-1].patrol_between_tunnels = [15, 11]
        self.players[-1].last_visited_tunnels = 11
        self.players.append(AIPlayer(550, 600, (255, 255, 255)))  # Patrolling w. flags.
        self.players[-1].patrol_between_tunnels = [20, 16]
        self.players[-1].last_visited_tunnels = 16

    def draw(self):
        """Drawing function for displaying earth, sky, tunnels, flags and players."""
        pygame.draw.rect(
            self.screen, EARTH_COLOR, (0, 200, WORLD_SIZE[0], WORLD_SIZE[1] - 200)
        )
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(self.screen, DARK_EARTH_COLOR, -6)
        pygame.draw.rect(self.screen, LIGHT_EARTH_COLOR, (0, 200, WORLD_SIZE[0], 6))
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(self.screen, LIGHT_EARTH_COLOR, 6)
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(self.screen, TUNNEL_COLOR, 0)
        pygame.draw.rect(self.screen, (200, 220, 255), (0, 0, WORLD_SIZE[0], 200))
        if self.debug_mode:
            for player in self.players:  # Using the design pattern "Iterator".
                if isinstance(player, AIPlayer):
                    path_len = len(player.current_path)
                    if path_len >= 2:
                        for i in range(path_len - 1):
                            pygame.draw.line(
                                self.screen,
                                player.color,
                                (
                                    self.tunnels[player.current_path[i]].end_x,
                                    self.tunnels[player.current_path[i]].end_y
                                    - TUNNEL_HGT / 2,
                                ),
                                (
                                    self.tunnels[player.current_path[i + 1]].end_x,
                                    self.tunnels[player.current_path[i + 1]].end_y
                                    - TUNNEL_HGT / 2,
                                ),
                                2,
                            )
            i = 0
            for tunnel in self.tunnels:  # Using the design pattern "Iterator".
                self.screen.blit(
                    self.font_small.render(str(i), True, (0, 255, 255)),
                    (tunnel.end_x, tunnel.end_y - TUNNEL_HGT / 2),
                )
                self.screen.blit(
                    self.font_small.render(
                        str(self.waypoint_net[str(i)])[1:-1], True, (255, 255, 255)
                    ),
                    (tunnel.end_x, tunnel.end_y - TUNNEL_HGT / 2 - 40),
                )
                i += 1
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (BUTTON_DEBUG_X, BUTTON_DEBUG_Y, BUTTON_DEBUG_WDT, BUTTON_DEBUG_HGT),
        )
        pygame.draw.rect(
            self.screen,
            (100, 160, 100),
            (
                BUTTON_DEBUG_X + 1,
                BUTTON_DEBUG_Y + 1,
                BUTTON_DEBUG_WDT - 2,
                BUTTON_DEBUG_HGT - 2,
            ),
        )
        self.screen.blit(self.text, (BUTTON_DEBUG_X + 10, BUTTON_DEBUG_Y + 10))
        self.screen.blit(self.text_goal, (BUTTON_DEBUG_X + 10, BUTTON_DEBUG_Y - 30))
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (BUTTON_RESET_X, BUTTON_RESET_Y, BUTTON_RESET_WDT, BUTTON_RESET_HGT),
        )
        pygame.draw.rect(
            self.screen,
            (100, 160, 100),
            (
                BUTTON_RESET_X + 1,
                BUTTON_RESET_Y + 1,
                BUTTON_RESET_WDT - 2,
                BUTTON_RESET_HGT - 2,
            ),
        )
        self.screen.blit(self.text_reset, (BUTTON_RESET_X + 10, BUTTON_RESET_Y + 10))
        for flag in self.flags:  # Using the design pattern "Iterator".
            flag.draw(self.screen)
        for player in self.players:  # Using the design pattern "Iterator".
            player.draw(self.screen)
        pygame.display.update()  # Update the display.


def sign(x) -> int:
    """Python and math have no standard function for sign()."""
    if x < 0:
        return -1
    else:
        return 1


def weightless_breadth_first_search(graph, start, end) -> []:
    """Finds the a list of nodes between two nodes. The function does not care about the distance
    between nodes (weights). Since the function could be useful for many use cases, it is not placed
    in the AIPlayer class."""
    queue = [[start]]
    visited = []
    # Return an empty list if the goal is already there.
    if start == end:
        return []
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in visited:
            for connected_nodes in graph[
                str(node)
            ]:  # Using the design pattern "Iterator".
                path_next = list(path)
                path_next.append(connected_nodes)
                queue.append(path_next)
                if connected_nodes == end:
                    return [*path_next]
            visited.append(node)
    # Return an empty list if there was no connection.
    return []


def main():
    """The main function of the game that contains a endless loop."""
    game_state = GameState()
    while True:
        game_state.clock.tick(FPS)  # Limit the game to a certain amount of FPS.
        for player in game_state.players:  # Using the design pattern "Iterator".
            if isinstance(player, AIPlayer):  # Apply pathfinding only to AIs.
                player.update(game_state)
            if isinstance(player, HumanPlayer):  # Applys input only to human players.
                reset = player.control_events(game_state)
                if reset:  # The reset needs to be called outside of control_events().
                    game_state = GameState()  # Reset all settings.
                    break  # Without break it can happen that the next AI player uses old waypoints.
            player.apply_speed(game_state)  # Apply speed to the player.
        game_state.draw()  # Drawing all objects in the techdemo.


if __name__ == "__main__":
    main()
