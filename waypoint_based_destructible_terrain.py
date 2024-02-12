"""
Project name: waypoint_based_destructible_terrain
Author: Armin Schäfer
Requirements: ```pip install pygame```
"""

# Standard Python libraries.
import math
import sys
from enum import Enum, auto

# Third-party libraries.
import pygame

# Constants.
FPS: int = 36
WINDOW_SIZE = (1000, 800)
EARTH_COLOR = (200, 130, 110)  # Brownish color.
LIGHT_EARTH_COLOR = (210, 140, 120)  # Lighter than EARTH_COLOR.
DARK_EARTH_COLOR = (190, 120, 100)  # Lighter than EARTH_COLOR.
TUNNEL_COLOR = (100, 30, 10)  # Should be darker than earth color.
SPEED_WALKING: float = (
    2.0  # Determines how fast he player is walking/jumping to left or right.
)
SPEED_DIGGING: float = (
    0.8  # Should be much lower than SPEEDWALKING to make it more realistic.
)
# This is only controling the vertical jumping speed. The horizontal jumping speed is SPEED_WALKING.
SPEED_JUMPING: float = 3.5
BUTTON_DEBUG_X: int = 10
BUTTON_DEBUG_Y: int = 45
BUTTON_DEBUG_WDT: int = 270
BUTTON_DEBUG_HGT: int = 40
BUTTON_RESET_X: int = 300
BUTTON_RESET_Y: int = 45
BUTTON_RESET_WDT: int = 100
BUTTON_RESET_HGT: int = 40
PLAYER_HGT: int = 20  # How tall is the player?
PLAYER_WDT: int = 10  # How wide is the player?
TUNNEL_HGT: int = 40  # The tunnel height should be at least as big as PLAYER_HGT.
DEGREE_45: float = (
    TUNNEL_HGT / 2 * math.sin(math.radians(45))
)  # This constant is needed for drawing the tunnels when a player diggs down.
DEGREE_22_X: float = (
    TUNNEL_HGT / 2 * math.sin(math.radians(22.5))
)  # This constant is needed for drawing the tunnels when a player diggs up.
DEGREE_22_Y: float = (
    TUNNEL_HGT / 2 * math.cos(math.radians(22.5))
)  # This constant is needed for drawing the tunnels when a player diggs up.


class Action(Enum):
    """Used by the class Player. There are three different actions a player can have."""

    FALLING = auto()
    WALKING = auto()
    DIGGING = auto()


class TunnelDirection(Enum):
    """Used by the class Player. A player can dig to six directions. We need an enum for this
    because we need to draw a tunnel depending on the direction of the tunnel."""

    FLAT = auto()
    RIGHTUP = auto()
    RIGHTDOWN = auto()
    LEFTUP = auto()
    LEFTDOWN = auto()


class Direction(Enum):
    """Used by the class Player. The direction the player is facing to."""

    LEFT = auto()
    RIGHT = auto()


class Player:
    """Player class which is the most important class in the techdemo."""

    action: Action
    direction: Direction
    x_position: float
    y_position: float
    color: ()
    x_speed: float
    y_speed: float
    last_visited_tunnel: int

    def __init__(self, x_position, y_position, color):
        self.action = (
            Action.FALLING
        )  # The default action is FALLING because the player may spawn mid-air.
        self.direction = Direction.LEFT
        self.x_position = x_position
        self.y_position = y_position
        self.color = color
        self.x_speed = 0
        self.y_speed = 0
        self.patrol_between_tunnels = []
        self.last_visited_tunnel = 0

    def command_start_digging(self, game_state):
        """Jump to the left."""
        if self.action in (Action.WALKING, Action.DIGGING):
            self.last_visited_tunnel = self.get_nearest_tunnel(game_state)
            self.action = Action.DIGGING
            game_state.tunnels.append(
                Tunnel(
                    self.x_position, self.y_position, self.x_position, self.y_position
                )
            )
            new_tunnel_id = len(game_state.tunnels) - 1
            # The new waypoint knows the last one.
            game_state.waypoint_net[str(new_tunnel_id)] = [self.last_visited_tunnel]
            # The last waypoint knows the new one.
            game_state.waypoint_net[str(self.last_visited_tunnel)].append(new_tunnel_id)
            # The player visits the new waypoint.
            self.last_visited_tunnel = new_tunnel_id

    def get_nearest_tunnel(self, game_state):
        """Gets a nearby tunnel. If none found, return last_visited_tunnel."""
        return self.last_visited_tunnel

    def command_stop_digging(self, game_state):
        """Not every time the player stops digging, this is called. Only if the player stops digging
        by using the corresponding key, this is called to make sure unneccesary tunnels get
        deleted."""
        amount_of_tunnels = len(game_state.tunnels)
        if self.action == Action.DIGGING and amount_of_tunnels > 2:
            if (
                game_state.tunnels[-1].start_x == game_state.tunnels[-1].end_x
            ):  # Check for tunnels with zero length.
                game_state.tunnels = game_state.tunnels[:-1]  # Delete latest tunnel.
                del game_state.waypoint_net[
                    str(amount_of_tunnels - 1)
                ]  # Delete the two latest waypoints.
                # Delete every reference to the new waypoint.
                for (
                    key
                ) in game_state.waypoint_net:  # Using the design pattern "Iterator".
                    if amount_of_tunnels - 1 in game_state.waypoint_net[key]:
                        game_state.waypoint_net[key].remove(amount_of_tunnels - 1)
            else:
                # Check if new connections are finished.
                tunnel_id = 0
                for tunnel in game_state.tunnels[
                    :-2
                ]:  # Using the design pattern "Iterator".
                    margin = TUNNEL_HGT
                    if (
                        tunnel.end_x - margin
                        <= self.x_position
                        <= tunnel.end_x + margin
                        and tunnel.end_y - margin
                        <= self.y_position
                        <= tunnel.end_y + margin
                    ):
                        # Combine the two waypoints close to each other.
                        game_state.waypoint_net[str(tunnel_id)].append(
                            amount_of_tunnels - 1
                        )
                        game_state.waypoint_net[str(amount_of_tunnels - 1)].append(
                            tunnel_id
                        )
                    tunnel_id += 1

    def command_stop(self):
        """If the player is walking, stop him."""
        if self.action in (Action.WALKING, Action.DIGGING):
            self.action = Action.WALKING
            self.x_speed = 0

    def command_jump_left(self):
        """Jump to the left."""
        if self.action == Action.WALKING:
            self.direction = Direction.LEFT
            self.action = Action.FALLING
            self.x_speed = -SPEED_WALKING
            self.y_speed = -SPEED_JUMPING

    def command_jump_right(self):
        """Jump to the right."""
        if self.action == Action.WALKING:
            self.direction = Direction.RIGHT
            self.action = Action.FALLING
            self.x_speed = SPEED_WALKING
            self.y_speed = -SPEED_JUMPING

    def command_walk_left(self):
        """Walk to the left."""
        self.direction = Direction.LEFT
        self.x_speed = -SPEED_WALKING

    def command_walk_right(self):
        """Walk to the right."""
        self.direction = Direction.RIGHT
        self.x_speed = SPEED_WALKING

    def is_there_solid_material(
        self, screen, x_position: float, y_position: float
    ) -> bool:
        """Returns True if there is earth at the given offset position."""
        return tuple(
            pygame.Surface.get_at(
                screen,
                (int(self.x_position + x_position), int(self.y_position + y_position)),
            )[:3]
        ) in [
            EARTH_COLOR, LIGHT_EARTH_COLOR
        ]

    def apply_speed(self, game_state):
        """Moves players on x- and y-axis."""
        if self.x_speed > 0:
            if self.is_there_solid_material(
                game_state.screen, 7, 0
            ) and self.is_there_solid_material(game_state.screen, 7, -20):
                self.x_speed = 0
            else:
                self.x_position += self.x_speed
        elif self.x_speed < 0:
            if self.is_there_solid_material(
                game_state.screen, -7, 0
            ) and self.is_there_solid_material(game_state.screen, -7, -20):
                self.x_speed = 0
            else:
                self.x_position += self.x_speed
        self.y_position += self.y_speed
        # The player should not leave the screen.
        if self.x_position < 10:
            self.x_position = 10
            self.action = Action.FALLING
        elif self.x_position >= WINDOW_SIZE[0] - 10:
            self.x_position = WINDOW_SIZE[0] - 11
            self.action = Action.FALLING
        if self.y_position < 0:
            self.y_position = 0
        elif self.y_position >= WINDOW_SIZE[1]:
            self.y_position = WINDOW_SIZE[1] - 1
        # Is the player falling?
        if self.action == Action.FALLING:
            # Gravitation.
            if self.y_speed < 10:
                if self.y_speed < -2:
                    self.y_speed += 0.075
                else:
                    self.y_speed += 0.5
            # Hit the ground?
            if self.y_speed > 0 and self.is_there_solid_material(
                game_state.screen, 0, 1
            ):
                self.x_speed = 0
                self.y_speed = 0
                self.action = Action.WALKING
            # Hit the ceiling with the head?
            if self.y_speed < 0 and (
                self.is_there_solid_material(game_state.screen, -5, -PLAYER_HGT)
                or self.is_there_solid_material(game_state.screen, 5, -PLAYER_HGT)
            ):
                self.x_speed = 0
                self.y_speed = 0
        if self.action == Action.WALKING:
            no_ground_below = False
            if self.x_speed != 0:
                if not self.is_there_solid_material(game_state.screen, 0, 1):
                    self.y_position += 1
                    if not self.is_there_solid_material(game_state.screen, 0, 1):
                        self.y_position += 1
                        if not self.is_there_solid_material(game_state.screen, 0, 1):
                            self.y_position += 1
                            if not self.is_there_solid_material(
                                game_state.screen, 0, 1
                            ):
                                self.y_position += 1
                                if not self.is_there_solid_material(
                                    game_state.screen, 0, 1
                                ):
                                    self.action = Action.FALLING
                    no_ground_below = True
                while (
                    self.is_there_solid_material(game_state.screen, -4, -2)
                    or self.is_there_solid_material(game_state.screen, 4, -2)
                ) and not no_ground_below:
                    self.y_position -= 1
        if self.action == Action.DIGGING:
            # Move the end of the latest tunnel segment to the player's position.
            game_state.tunnels[-1].end_x = self.x_position
            game_state.tunnels[-1].end_y = self.y_position
            # The player should fall down while digging when there is no earth below.
            if not self.is_there_solid_material(
                game_state.screen, 0, 4
            ) and not self.is_there_solid_material(game_state.screen, 0, 1):
                if (
                    self.y_speed > 0
                ):  # Falling down while digging down? Open up tunnel even more.
                    game_state.tunnels[self.last_visited_tunnel].end_x += (
                        TUNNEL_HGT / 2 * self.x_speed
                    )
                    game_state.tunnels[self.last_visited_tunnel].end_y += (
                        TUNNEL_HGT / 2 * self.y_speed
                    )
                self.command_stop_digging(game_state)
                self.action = Action.FALLING

    def draw(self, screen):
        """Draws a player to screen."""
        hgt = PLAYER_HGT
        wdt = PLAYER_WDT
        # Left leg.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 2),
            (self.x_position - wdt / 2, self.y_position),
            2,
        )
        # Right leg.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 2),
            (self.x_position + wdt / 2, self.y_position),
            2,
        )
        # Spine.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 3),
            (self.x_position, self.y_position - hgt),
            2,
        )
        # Arms.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 3 * 2),
            (
                self.x_position
                + wdt / 2 * (1 if self.direction == Direction.RIGHT else -1),
                self.y_position
                - (hgt / 5 * 4 if self.action == Action.FALLING else hgt / 3 * 2),
            ),
            2,
        )
        # Head.
        pygame.draw.circle(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt),
            wdt / 2,
        )
        # Digging? If yes, draw a shovel.
        if self.action == Action.DIGGING:
            pygame.draw.line(
                screen,
                (255, 100, 10),
                (
                    self.x_position
                    - wdt / 2 * (1 if self.direction == Direction.RIGHT else -1),
                    self.y_position - 5,
                ),
                (
                    self.x_position
                    + wdt * (1 if self.direction == Direction.RIGHT else -1),
                    self.y_position - hgt + pygame.time.get_ticks() % 4,
                ),
                2,
            )
            pygame.draw.circle(
                screen,
                (100, 100, 100),
                (
                    self.x_position
                    + wdt * (1 if self.direction == Direction.RIGHT else -1),
                    self.y_position - hgt + pygame.time.get_ticks() % 4,
                ),
                wdt / 2,
            )


class Flag:
    """Visual checkpoint."""

    x_position: float
    y_position: float
    color: []

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


class Tunnel:
    """Visual hole in the earth."""

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


class HumanPlayer(Player):
    """Subclass of Player. A human player can be controlled via keyboard."""

    def control_events(self, game_state):
        """Listens to keyboard and mouse inputs."""
        event_list = pygame.event.get()
        for event in event_list:  # Using the design pattern "Iterator".
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if (
                    BUTTON_DEBUG_X <= mouse[0] <= BUTTON_DEBUG_X + BUTTON_DEBUG_WDT
                    and BUTTON_DEBUG_Y <= mouse[1] <= BUTTON_DEBUG_Y + BUTTON_DEBUG_HGT
                ):
                    game_state.debug_mode = not game_state.debug_mode
                    if game_state.debug_mode:
                        game_state.text = game_state.font_big.render(
                            "Turn off debug mode", True, (0, 0, 0)
                        )
                    else:
                        game_state.text = game_state.font_big.render(
                            "Turn on debug mode", True, (0, 0, 0)
                        )
                if (
                    BUTTON_RESET_X <= mouse[0] <= BUTTON_RESET_X + BUTTON_RESET_WDT
                    and BUTTON_RESET_Y <= mouse[1] <= BUTTON_RESET_Y + BUTTON_RESET_HGT
                ):
                    return True
            if event.type == pygame.KEYDOWN:
                if (
                    event.key in (pygame.K_RCTRL, pygame.K_LCTRL)
                ) and self.action == Action.WALKING:
                    self.command_start_digging(game_state)
                elif (
                    event.key in (pygame.K_RCTRL, pygame.K_LCTRL)
                ) and self.action == Action.DIGGING:
                    self.command_stop_digging(game_state)
                    self.command_stop()
                elif event.key == pygame.K_LEFT and self.action == Action.WALKING:
                    self.command_walk_left()
                elif event.key == pygame.K_RIGHT and self.action == Action.WALKING:
                    self.command_walk_right()
                elif (
                    event.key == pygame.K_RIGHT and self.action == Action.DIGGING
                ):  # Digging to RIGHT.
                    self.command_start_digging(game_state)
                    game_state.tunnels[-1].direction = TunnelDirection.FLAT
                    self.direction = Direction.RIGHT
                    self.x_speed = SPEED_DIGGING
                    self.y_speed = 0
                elif (
                    event.key == pygame.K_LEFT and self.action == Action.DIGGING
                ):  # Digging to LEFT.
                    self.command_start_digging(game_state)
                    game_state.tunnels[-1].direction = TunnelDirection.FLAT
                    self.direction = Direction.LEFT
                    self.x_speed = -SPEED_DIGGING
                    self.y_speed = 0
                elif event.key == pygame.K_UP and self.action == Action.DIGGING:
                    self.command_start_digging(game_state)
                    if self.direction == Direction.RIGHT:  # Digging to RIGHT UP.
                        self.x_speed = SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.RIGHTUP
                    else:  # Digging to LEFT UP.
                        self.x_speed = -SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.LEFTUP
                    self.y_speed = -SPEED_DIGGING / 2
                elif event.key == pygame.K_DOWN and self.action == Action.DIGGING:
                    self.command_start_digging(game_state)
                    if self.direction == Direction.RIGHT:  # Digging to RIGHT DOWN.
                        self.x_speed = SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.RIGHTDOWN
                    else:  # Digging to LEFT DOWN.
                        self.x_speed = -SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.LEFTDOWN
                    self.y_speed = SPEED_DIGGING
                elif event.key == pygame.K_UP and self.action == Action.WALKING:
                    if self.direction == Direction.LEFT:
                        self.command_jump_left()
                    else:
                        self.command_jump_right()
            if event.type == pygame.KEYUP:
                if (
                    event.key in (pygame.K_LEFT, pygame.K_RIGHT)
                ) and self.action == Action.WALKING:
                    self.command_stop()
                if (
                    event.key
                    in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)
                    and self.action == Action.DIGGING
                ):
                    self.x_speed = 0
                    self.y_speed = 0


class AIPlayer(Player):
    """Subclass of Player. An AIPlayer has the ability to patrol between spots."""

    patrol_between_tunnels: []
    current_path: []

    def update(self, game_state):
        """Update the patrol path in AIs."""
        # Does the AI have a patrol task?
        if len(self.patrol_between_tunnels) < 2 or self.action != Action.WALKING:
            return
        path = weightless_breadth_first_search(
            game_state.waypoint_net,
            self.last_visited_tunnel,
            self.patrol_between_tunnels[0],
        )
        self.current_path = path
        if len(path) > 0:
            next_node = path[1]
            if (
                game_state.tunnels[next_node].end_x > self.x_position
                and game_state.tunnels[next_node].end_x
                > game_state.tunnels[self.last_visited_tunnel].end_x
            ):
                if self.x_speed == 0 and (
                    (
                        game_state.tunnels[self.last_visited_tunnel].end_y
                        > game_state.tunnels[next_node].end_y
                        and not self.is_there_solid_material(game_state.screen, 10, -1)
                    )
                    or (
                        game_state.tunnels[self.last_visited_tunnel].end_y
                        == game_state.tunnels[next_node].end_y
                        and not self.is_there_solid_material(game_state.screen, 10, 1)
                        and game_state.tunnels[next_node].end_x
                        > self.x_position + TUNNEL_HGT
                    )
                ):
                    self.command_jump_right()
                self.command_walk_right()
            elif (
                game_state.tunnels[next_node].end_x < self.x_position
                and game_state.tunnels[next_node].end_x
                < game_state.tunnels[self.last_visited_tunnel].end_x
            ):
                if self.x_speed == 0 and (
                    (
                        game_state.tunnels[self.last_visited_tunnel].end_y
                        > game_state.tunnels[next_node].end_y
                        and not self.is_there_solid_material(game_state.screen, -10, -1)
                    )
                    or (
                        game_state.tunnels[self.last_visited_tunnel].end_y
                        == game_state.tunnels[next_node].end_y
                        and not self.is_there_solid_material(game_state.screen, -10, 1)
                        and game_state.tunnels[next_node].end_x
                        < self.x_position - TUNNEL_HGT
                    )
                ):
                    self.command_jump_left()
                self.command_walk_left()
            else:
                self.command_stop()
                self.last_visited_tunnel = next_node
                if self.last_visited_tunnel == self.patrol_between_tunnels[0]:
                    self.patrol_between_tunnels = self.patrol_between_tunnels[1:] + [
                        self.patrol_between_tunnels[0]
                    ]


class GameState:
    """Contains all important infos about the game."""

    pygame: pygame
    screen: pygame.display
    clock: pygame.time.Clock
    debug_mode: bool
    font_big: pygame.font.Font
    font_medium: pygame.font.Font
    font_small: pygame.font.Font
    text: pygame.Surface
    text_reset: pygame.Surface
    text_goal: pygame.Surface
    flags = []
    tunnels = []
    players = []
    waypoint_net = {}

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("waypoint based destructible terrain")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.debug_mode = False
        self.font_big = pygame.font.SysFont("Corbel", 35)
        self.font_medium = pygame.font.SysFont("Corbel", 22)
        self.font_small = pygame.font.SysFont("Corbel", 20)
        self.text = self.font_big.render("Turn on debug mode", True, (0, 0, 0))
        self.text_reset = self.font_big.render("Reset", True, (0, 0, 0))
        self.text_goal = self.font_medium.render(
            "Move via arrow keys. Start/end digging via left or right Control. Dig a tunnel to the \
red flag to make the AI move between the red flags.",
            True,
            (0, 0, 0),
        )

        # Place flags.
        self.flags = []
        self.flags.append(Flag(100, 300, (255, 0, 0)))  # Red flag.
        self.flags.append(Flag(720, 500, (255, 0, 0)))  # Red flag.
        self.flags.append(Flag(100, 500, (255, 255, 0)))  # Yellow flag.
        self.flags.append(Flag(300, 700, (255, 255, 0)))  # Yellow flag.
        self.flags.append(Flag(300, 500, (0, 255, 0)))  # Green flag.
        self.flags.append(Flag(50, 700, (0, 255, 0)))  # Green flag.

        # Place some tunnels connecting the flags. Since the tunnels are placed manually, the
        # waypoint net must be filled manually.
        self.tunnels = []
        self.tunnels.append(
            Tunnel(100, 300, 100, 300)
        )  # Tunnel at the red flags. ID = 0.
        self.tunnels.append(
            Tunnel(100, 300, 600, 300)
        )  # Tunnel at the red flags. ID = 1.
        self.tunnels.append(
            Tunnel(680, 500, 680, 500)
        )  # Tunnel at the red flags. ID = 2.
        self.tunnels.append(
            Tunnel(680, 500, 720, 500)
        )  # Tunnel at the red flags. ID = 3.
        self.tunnels.append(
            Tunnel(100, 500, 100, 500)
        )  # Tunnel for yellow flags. Top left. ID = 4.
        self.tunnels.append(
            Tunnel(100, 500, 200, 600)
        )  # Tunnel for yellow flags. Middle. ID = 5.
        self.tunnels.append(
            Tunnel(200, 600, 300, 700)
        )  # Tunnel for yellow flags. Bottom right. ID = 6.
        self.tunnels.append(
            Tunnel(300, 500, 300, 500)
        )  # Tunnel for green flags. Top right. ID = 7.
        self.tunnels.append(
            Tunnel(300, 500, 200, 600)
        )  # Tunnel for green flags. Middle. ID = 8.
        self.tunnels.append(
            Tunnel(200, 600, 100, 700)
        )  # Tunnel for green flags. Bottom left. ID = 9.
        self.tunnels.append(
            Tunnel(100, 700, 50, 700)
        )  # Tunnel for green flags. Bottom left. ID = 10.

        # Waypoint net that knows which tunnels are connected.
        self.waypoint_net = {
            "0": [1],
            "1": [0],
            "2": [3],
            "3": [2],
            "4": [5],
            "5": [4, 6, 7, 9],
            "6": [5],
            "7": [8],
            "8": [4, 6, 7, 9],
            "9": [8, 10],
            "10": [9],
        }

        # Place players.
        self.players = []
        self.players.append(HumanPlayer(300, 300, (255, 100, 0)))  # Human player.
        self.players.append(AIPlayer(700, 500, (255, 0, 0)))  # AI patrolling red flags.
        self.players[-1].patrol_between_tunnels = [0, 3]
        self.players[-1].last_visited_tunnel = 3
        self.players.append(
            AIPlayer(100, 500, (255, 255, 0))
        )  # AI patrolling yellow flags.
        self.players[-1].patrol_between_tunnels = [6, 4]
        self.players[-1].last_visited_tunnel = 4
        self.players.append(
            AIPlayer(300, 500, (0, 255, 0))
        )  # AI patrolling green flags.
        self.players[-1].patrol_between_tunnels = [10, 7]
        self.players[-1].last_visited_tunnel = 7

    def draw(self):
        """Drawing function for displaying earth, sky, tunnels, flags and players."""
        pygame.draw.rect(self.screen, EARTH_COLOR, (0, 200, WINDOW_SIZE[0], 700))
        pygame.draw.rect(self.screen, LIGHT_EARTH_COLOR, (0, 200, WINDOW_SIZE[0], 6))
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(self.screen, DARK_EARTH_COLOR, -6)
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(self.screen, LIGHT_EARTH_COLOR, 6)
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(self.screen, TUNNEL_COLOR, 0)
        for tunnel in self.tunnels:  # Using the design pattern "Iterator".
            if self.debug_mode:
                pygame.draw.line(
                    self.screen,
                    (255,255,255),
                    (
                        tunnel.start_x,
                        tunnel.start_y
                        - TUNNEL_HGT / 2,
                    ),
                    (
                        tunnel.end_x,
                        tunnel.end_y
                        - TUNNEL_HGT / 2,
                    ),
                    1,
                )
        pygame.draw.rect(self.screen, (200, 220, 255), (0, 0, WINDOW_SIZE[0], 200))
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
                    self.font_small.render(str(i), True, (255, 255, 255)),
                    (tunnel.end_x, tunnel.end_y - TUNNEL_HGT / 2),
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
