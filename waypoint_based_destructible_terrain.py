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


def sign(x) -> int:
    if x < 0:
        return -1
    else:
        return 1


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
    x_position: int
    y_position: int
    color: ()
    x_speed: float
    y_speed: float
    last_visited_tunnels: []

    def __init__(self, x_position, y_position, color):
        # The default action is Action.FALLING because the player may spawn mid-air.
        # He will fall down anyway because of gravitation and will continue to be in Action.WALKING.
        self.action = Action.FALLING
        self.direction = Direction.LEFT
        self.x_position = x_position
        self.y_position = y_position
        self.color = color
        self.x_speed = 0
        self.y_speed = 0
        self.patrol_between_tunnels = [0]
        self.last_visited_tunnels = []

    def command_start_digging(self, game_state):
        """Start digging a tunnel in the landscape."""
        if self.action in (Action.WALKING, Action.DIGGING):
            # Just startet digging?
            if self.action == Action.WALKING:
                self.last_visited_tunnels = self.find_tunnel_we_are_in(game_state)
                if self.last_visited_tunnels == []:
                    self.last_visited_tunnels = self.get_nearest_tunnel(game_state)
            game_state.tunnels.append(
                Tunnel(
                    self.x_position, self.y_position, self.x_position, self.y_position
                )
            )
            new_tunnel_id = len(game_state.tunnels) - 1
            game_state.waypoint_net[str(new_tunnel_id)] = set()
            for i in range(len(self.last_visited_tunnels)):
                adding_now = self.last_visited_tunnels[i]
                # The new waypoint knows the last one.
                game_state.waypoint_net[str(new_tunnel_id)].add(adding_now)
                # The last waypoint knows the new one.
                game_state.waypoint_net[str(self.last_visited_tunnels[i])].add(
                    new_tunnel_id
                )
                if (
                    len(self.last_visited_tunnels) == 2
                    and self.last_visited_tunnels[i - 1]
                    in game_state.waypoint_net[str(self.last_visited_tunnels[i])]
                ):
                    game_state.waypoint_net[str(self.last_visited_tunnels[i])].remove(
                        self.last_visited_tunnels[i - 1]
                    )
            # The player visits the new waypoint.
            self.last_visited_tunnels = [new_tunnel_id]
            self.action = Action.DIGGING

    def get_nearest_tunnel(self, game_state) -> []:
        """Gets a nearby tunnel. If none found, return self.last_visited_tunnels."""
        tunnel_id = 0
        for tunnel in game_state.tunnels:  # Using the design pattern "Iterator".
            margin = TUNNEL_HGT
            if (
                tunnel.end_x - margin <= self.x_position <= tunnel.end_x + margin
                and tunnel.end_y - margin <= self.y_position <= tunnel.end_y + margin
            ):
                return [tunnel_id]
            tunnel_id += 1
        return self.last_visited_tunnels

    def find_tunnel_we_are_in(self, game_state):
        """This function will give you the two tunnels you are inbetween with. TODO"""
        x = math.floor(self.x_position)
        y = math.floor(self.y_position)
        tunnel_id = 0
        hits = set()
        for tunnel in game_state.tunnels:
            if y == math.floor(tunnel.start_y) and y == math.floor(tunnel.end_y):
                hits.add(tunnel_id)
            else:
                x1 = math.floor(tunnel.start_x)
                y1 = math.floor(tunnel.start_y)
                x2 = math.floor(tunnel.end_x)
                y2 = math.floor(tunnel.end_y)
                # The following six lines are very hacky. Could be better but requires lots of work!
                y_offset = 8 if x2 < x1 else 6
                a = math.fabs(x - x1)
                b = math.fabs((y - y_offset) - y1)
                c = math.fabs(x - x2)
                d = math.fabs((y - y_offset) - y2)
                erg = (a == b or a == (b - 2)) and (c == d or c == (d - 2))
                if erg:
                    hits.add(tunnel_id)
            tunnel_id += 1

        # Remove wrong hits on the right side of x.
        right_side_min_id = None
        right_side_min = 100000
        removing = []
        for hit in hits:
            if (
                game_state.tunnels[hit].end_x > self.x_position
            ):  # Is the tunnel_end on the right side at all?
                if game_state.tunnels[hit].end_x < right_side_min:  # Is it very near?
                    if right_side_min_id != None:
                        removing.append(right_side_min_id)
                    right_side_min_id = hit
                    right_side_min = game_state.tunnels[hit].end_x
                else:
                    removing.append(hit)
        for remove in removing:
            hits.remove(remove)

        # Remove wrong hits on the left side of x.
        left_side_max_id = None
        left_side_max = -100000
        removing = []
        for hit in hits:
            if (
                game_state.tunnels[hit].end_x < self.x_position
            ):  # Is the tunnel_end on the left side at all?
                if game_state.tunnels[hit].end_x > left_side_max:  # Is it very near?
                    if left_side_max_id != None:
                        removing.append(left_side_max_id)
                    left_side_max_id = hit
                    left_side_max = game_state.tunnels[hit].end_x
                else:
                    removing.append(hit)
        for remove in removing:
            hits.remove(remove)

        # If all tunnel ends were on only one side, we found nothing.
        if len(hits) < 2:
            return []

        # Check if the tunnel ends are even connected by the waypoint_net.
        hits_list = list(hits)
        if (
            hits_list[0] in game_state.waypoint_net[str(hits_list[1])]
            or hits_list[1] in game_state.waypoint_net[str(hits_list[0])]
        ):
            return hits_list
        else:
            return []

    def command_stop_digging(self, game_state):
        """When the player stops digging, the waypoints search for new connections."""
        amount_of_tunnels = len(game_state.tunnels)
        if self.action == Action.DIGGING and amount_of_tunnels > 2:
            # Check if new connections are finished.
            tunnel_id = self.get_nearest_tunnel(game_state)[0]
            # Combine the two waypoints close to each other.
            if tunnel_id != self.last_visited_tunnels[0]:
                game_state.waypoint_net[str(tunnel_id)].add(amount_of_tunnels - 1)
                game_state.waypoint_net[str(amount_of_tunnels - 1)].add(tunnel_id)

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
        ) in [EARTH_COLOR, LIGHT_EARTH_COLOR]

    def unstuck(self):
        pass

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
        elif self.x_position >= WORLD_SIZE[0] - 10:
            self.x_position = WORLD_SIZE[0] - 11
            self.action = Action.FALLING
        if self.y_position < 0:
            self.y_position = 0
        elif self.y_position >= WORLD_SIZE[1]:
            self.y_position = WORLD_SIZE[1] - 1
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
                self.x_position = math.floor(self.x_position)
                self.y_position = math.floor(self.y_position)
            # Hit the ceiling with the head?
            if self.y_speed < 0 and (
                self.is_there_solid_material(game_state.screen, -5, -PLAYER_HGT)
                or self.is_there_solid_material(game_state.screen, 5, -PLAYER_HGT)
            ):
                self.x_speed = 0
                self.y_speed = 0
        if self.action == Action.WALKING:
            self.y_position = math.floor(self.y_position)
            if self.x_speed != 9990:  # eig 0
                if not self.is_there_solid_material(game_state.screen, 0, 1):
                    self.y_position = math.floor(self.y_position + 1)
                    if not self.is_there_solid_material(game_state.screen, 0, 1):
                        self.y_position = math.floor(self.y_position + 1)
                        if not self.is_there_solid_material(game_state.screen, 0, 1):
                            self.y_position = math.floor(self.y_position + 1)
                            if not self.is_there_solid_material(
                                game_state.screen, 0, 1
                            ):
                                self.y_position = math.floor(self.y_position + 1)
                                if not self.is_there_solid_material(
                                    game_state.screen, 0, 1
                                ):
                                    self.action = Action.FALLING
                while self.is_there_solid_material(game_state.screen, 0, 0):
                    self.y_position = math.floor(self.y_position - 1)
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
                    game_state.tunnels[self.last_visited_tunnels[0]].end_x += (
                        TUNNEL_HGT / 2 * self.x_speed
                    )
                    game_state.tunnels[self.last_visited_tunnels[0]].end_y += (
                        TUNNEL_HGT / 2 * self.y_speed
                    )
                self.command_stop_digging(game_state)
                self.action = Action.FALLING

    def draw(self, screen):
        """Draws a player to screen."""
        hgt = PLAYER_HGT
        wdt = PLAYER_WDT
        # Draw left leg.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 2),
            (self.x_position - wdt / 2, self.y_position),
            2,
        )
        # Draw right leg.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 2),
            (self.x_position + wdt / 2, self.y_position),
            2,
        )
        # Draw spine.
        pygame.draw.line(
            screen,
            self.color,
            (self.x_position, self.y_position - hgt / 3),
            (self.x_position, self.y_position - hgt),
            2,
        )
        # Draw arms. The player is holding both arms out towards the direction he is looking! :)
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
        # Draw head.
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
    """Visual checkpoint that is only used for decoration."""

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
                elif event.key == pygame.K_RIGHT and self.action == Action.DIGGING:
                    # Digging to RIGHT.
                    self.command_start_digging(game_state)
                    game_state.tunnels[-1].direction = TunnelDirection.FLAT
                    self.direction = Direction.RIGHT
                    self.x_speed = SPEED_DIGGING
                    self.y_speed = 0
                elif event.key == pygame.K_LEFT and self.action == Action.DIGGING:
                    # Digging to LEFT.
                    self.command_start_digging(game_state)
                    game_state.tunnels[-1].direction = TunnelDirection.FLAT
                    self.direction = Direction.LEFT
                    self.x_speed = -SPEED_DIGGING
                    self.y_speed = 0
                elif event.key == pygame.K_UP and self.action == Action.DIGGING:
                    self.command_start_digging(game_state)
                    if self.direction == Direction.RIGHT:
                        # Digging to RIGHT UP.
                        self.x_speed = SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.RIGHTUP
                    else:
                        # Digging to LEFT UP.
                        self.x_speed = -SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.LEFTUP
                    self.y_speed = -SPEED_DIGGING / 2
                elif event.key == pygame.K_DOWN and self.action == Action.DIGGING:
                    self.command_start_digging(game_state)
                    if self.direction == Direction.RIGHT:
                        # Digging to RIGHT DOWN.
                        self.x_speed = SPEED_DIGGING
                        game_state.tunnels[-1].direction = TunnelDirection.RIGHTDOWN
                    else:
                        # Digging to LEFT DOWN.
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
            self.last_visited_tunnels,
            self.patrol_between_tunnels[0],
        )
        self.current_path = path
        if len(path) > 0:
            next_node = path[1]
            if (
                game_state.tunnels[next_node].end_x > self.x_position
                and game_state.tunnels[next_node].end_x
                > game_state.tunnels[self.last_visited_tunnels].end_x
            ):
                if self.x_speed == 0 and (
                    (
                        game_state.tunnels[self.last_visited_tunnels].end_y
                        > game_state.tunnels[next_node].end_y
                        and not self.is_there_solid_material(game_state.screen, 10, -1)
                    )
                    or (
                        game_state.tunnels[self.last_visited_tunnels].end_y
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
                < game_state.tunnels[self.last_visited_tunnels].end_x
            ):
                if self.x_speed == 0 and (
                    (
                        game_state.tunnels[self.last_visited_tunnels].end_y
                        > game_state.tunnels[next_node].end_y
                        and not self.is_there_solid_material(game_state.screen, -10, -1)
                    )
                    or (
                        game_state.tunnels[self.last_visited_tunnels].end_y
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
                self.last_visited_tunnels = next_node
                if self.last_visited_tunnels == self.patrol_between_tunnels[0]:
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
    waypoint_net = dict()

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("waypoint based destructible terrain")
        self.screen = pygame.display.set_mode(DEFAULT_WINDOW_SIZE, pygame.RESIZABLE)
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
