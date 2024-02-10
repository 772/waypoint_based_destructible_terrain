"""
Project name: waypoint_based_destructible_terrain
Author: Armin Schäfer
Requirements: ```pip install pygame```
"""

# Standard libraries.
import math
import random
from enum import Enum, auto

# Third-party libraries.
import pygame

# Constants.
WINDOW_SIZE = (1000, 800)
EARTH_COLOR = (200, 130, 110)
TUNNEL_COLOR = (100, 30, 10)
SPEED_WALKING: float = 2.0
SPEED_DIGGING: float = 0.8
SPEED_JUMPING: float = 7.0
BUTTON_DEBUG_X: int = 10
BUTTON_DEBUG_Y: int = 10
BUTTON_DEBUG_WDT: int = 270
BUTTON_DEBUG_HGT: int = 40
BUTTON_RESET_X: int = 300
BUTTON_RESET_Y: int = 10
BUTTON_RESET_WDT: int = 100
BUTTON_RESET_HGT: int = 40
TUNNEL_HGT: int = 40
PLAYER_HGT: int = 20
AI_TIMER: int = 40  # Only control AI every 40 frames.
DEGREE_45: float = TUNNEL_HGT / 2 * math.sin(math.radians(45))
DEGREE_22_X: float = TUNNEL_HGT / 2 * math.sin(math.radians(22.5))
DEGREE_22_Y: float = TUNNEL_HGT / 2 * math.cos(math.radians(22.5))


class Action(Enum):
    """Used by the class Player."""

    FALLING = auto()
    WALKING = auto()
    DIGGING = auto()


class TunnelDirection(Enum):
    """Used by the class Player."""

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
    """Player."""

    action: Action
    direction: Direction
    x: float
    y: float
    x_speed: float
    y_speed: float
    last_visited_tunnel: int

    def __init__(self, x, y):
        self.action = (
            Action.FALLING
        )  # The default action is FALLING because the player may spawn mid-air.
        self.direction = Direction.LEFT
        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0
        self.patrol_between_tunnels = []
        self.last_visited_tunnel = 0

    def command_start_digging(self, tunnels, waypoint_net):
        """Jump to the left."""
        if self.action == Action.WALKING or self.action == Action.DIGGING:
            amount_of_tunnels = len(tunnels)
            if self.action == Action.DIGGING:
                if amount_of_tunnels > 1:
                    pass
                    # TODO: Connect the latest two tunnels?
            self.action = Action.DIGGING
            tunnels.append(Tunnel(self.x, self.y, self.x, self.y))
            waypoint_net[str(len(tunnels) - 1)] = []

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

    def command_stop(self):
        """If the player is walking, stop him."""
        if self.action == Action.WALKING or self.action == Action.DIGGING:
            self.action = Action.WALKING
            self.x_speed = 0

    def is_there_solid_material(self, screen, x: float, y: float) -> bool:
        """Returns True if there is earth at the given offset position."""
        return tuple(
            pygame.Surface.get_at(screen, (int(self.x + x), int(self.y + y)))[:3]
        ) not in [
            TUNNEL_COLOR,
            (255, 0, 0),
            (255, 255, 0),
            (0, 255, 0),
            (255, 255, 255),
        ]

    def draw(self, screen):
        player_color = (255, 0, 0)
        if self.action == Action.DIGGING:
            player_color = (255, 255, 0)
        pygame.draw.polygon(
            screen,
            player_color,
            (
                (self.x + 3, self.y),
                (self.x + 2, self.y - 18),
                (self.x - 2, self.y - 18),
                (self.x - 3, self.y),
                (self.x - 5, self.y - 20),
                (self.x + 5, self.y - 20),
            ),
            0,
        )


class Flag:
    """Visual checkpoint."""

    x: float
    y: float
    color: []

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, screen):
        pygame.draw.polygon(
            screen,
            self.color,
            (
                (self.x, self.y),
                (self.x, self.y - 25),
                (self.x + 10, self.y - 20),
                (self.x + 2, self.y - 15),
                (self.x + 2, self.y),
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

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            TUNNEL_COLOR,
            (self.end_x, self.end_y - TUNNEL_HGT / 2),
            TUNNEL_HGT / 2,
        )
        if self.direction == TunnelDirection.FLAT:
            pygame.draw.polygon(
                screen,
                TUNNEL_COLOR,
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
                TUNNEL_COLOR,
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
                TUNNEL_COLOR,
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
                TUNNEL_COLOR,
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
                TUNNEL_COLOR,
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


class HumanPlayer(Player):
    pass


class AIPlayer(Player):
    patrol_between_tunnels: []


def main():
    pygame.init()
    pygame.display.set_caption("waypoint based destructible terrain")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    debug_mode = False
    smallfont = pygame.font.SysFont("Corbel", 35)
    smallfont2 = pygame.font.SysFont("Corbel", 22)
    tiny_font = pygame.font.SysFont("Corbel", 20)
    text = smallfont.render("Turn on debug mode", True, (0, 0, 0))
    text_reset = smallfont.render("Reset", True, (0, 0, 0))
    text2 = smallfont2.render(
        "Move via arrow keys. Start/end digging via left or right Control. Dig a tunnel to the red flag to make the AI move between the red flags.",
        True,
        (0, 0, 0),
    )
    ai_timer = AI_TIMER
    flags = []
    tunnels = []
    players = []
    waypoint_net = {}

    # Place flags.
    flags.append(Flag(100, 200, (255, 0, 0)))  # Red flag.
    flags.append(Flag(720, 400, (255, 0, 0)))  # Red flag.
    flags.append(Flag(100, 400, (255, 255, 0)))  # Yellow flag.
    flags.append(Flag(300, 600, (255, 255, 0)))  # Yellow flag.
    flags.append(Flag(300, 400, (0, 255, 0)))  # Green flag.
    flags.append(Flag(50, 600, (0, 255, 0)))  # Green flag.

    # Place some tunnels connecting the flags. Since the tunnels are placed manually, the waypoint net must be filled manually.
    tunnels.append(Tunnel(100, 200, 100, 200))  # Tunnel at the red flags. ID = 0.
    tunnels.append(Tunnel(100, 200, 900, 200))  # Tunnel at the red flags. ID = 1.
    tunnels.append(Tunnel(680, 400, 680, 400))  # Tunnel at the red flags. ID = 2.
    tunnels.append(Tunnel(680, 400, 720, 400))  # Tunnel at the red flags. ID = 3.
    tunnels.append(
        Tunnel(100, 400, 100, 400)
    )  # Tunnel for yellow flags. Top left. ID = 4.
    tunnels.append(
        Tunnel(100, 400, 200, 500)
    )  # Tunnel for yellow flags. Middle. ID = 5.
    tunnels.append(
        Tunnel(200, 500, 300, 600)
    )  # Tunnel for yellow flags. Bottom right. ID = 6.
    tunnels.append(
        Tunnel(300, 400, 300, 400)
    )  # Tunnel for green flags. Top right. ID = 7.
    tunnels.append(
        Tunnel(300, 400, 200, 500)
    )  # Tunnel for green flags. Middle. ID = 8.
    tunnels.append(
        Tunnel(200, 500, 100, 600)
    )  # Tunnel for green flags. Bottom left. ID = 9.
    tunnels.append(
        Tunnel(100, 600, 50, 600)
    )  # Tunnel for green flags. Bottom left. ID = 10.
    waypoint_net["0"] = [1]
    waypoint_net["1"] = [0]
    waypoint_net["2"] = [3]
    waypoint_net["3"] = [2]
    waypoint_net["4"] = [5]
    waypoint_net["5"] = [4, 6, 7, 9]
    waypoint_net["6"] = [5]
    waypoint_net["7"] = [8]
    waypoint_net["8"] = [4, 6, 7, 9]
    waypoint_net["9"] = [8, 10]
    waypoint_net["10"] = [9]

    # Place players.
    players.append(HumanPlayer(500, 200))  # Human player.
    players.append(AIPlayer(700, 400))  # AI patrolling red flags.
    players[-1].patrol_between_tunnels = [0, 3]
    players[-1].last_visited_tunnel = 3
    players.append(AIPlayer(100, 400))  # AI patrolling yellow flags.
    players[-1].patrol_between_tunnels = [6, 4]
    players[-1].last_visited_tunnel = 4
    players.append(AIPlayer(300, 400))  # AI patrolling green flags.
    players[-1].patrol_between_tunnels = [10, 7]
    players[-1].last_visited_tunnel = 7

    while True:
        # Limit the game to 36 FPS.
        clock.tick(36)
        # Limit the AI actions even more to reduce the number of computations.
        ai_timer = ai_timer - 1 if ai_timer > 0 else AI_TIMER

        for player in players:  # Using the design pattern "Iterator".
            # Keyboard and mouse input for human players.
            if type(player) == HumanPlayer:
                event_list = pygame.event.get()
                for event in event_list:  # Using the design pattern "Iterator".
                    if event.type == pygame.QUIT:
                        exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        if (
                            BUTTON_DEBUG_X
                            <= mouse[0]
                            <= BUTTON_DEBUG_X + BUTTON_DEBUG_WDT
                            and BUTTON_DEBUG_Y
                            <= mouse[1]
                            <= BUTTON_DEBUG_Y + BUTTON_DEBUG_HGT
                        ):
                            debug_mode = not debug_mode
                            if debug_mode:
                                text = smallfont.render(
                                    "Turn off debug mode", True, (0, 0, 0)
                                )
                            else:
                                text = smallfont.render(
                                    "Turn on debug mode", True, (0, 0, 0)
                                )
                        if (
                            BUTTON_RESET_X
                            <= mouse[0]
                            <= BUTTON_RESET_X + BUTTON_RESET_WDT
                            and BUTTON_RESET_Y
                            <= mouse[1]
                            <= BUTTON_RESET_Y + BUTTON_RESET_HGT
                        ):
                            main()
                    if event.type == pygame.KEYDOWN:
                        if (
                            event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL
                        ) and player.action == Action.WALKING:
                            player.command_start_digging(tunnels, waypoint_net)
                        elif (
                            event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL
                        ) and player.action == Action.DIGGING:
                            player.command_stop()
                        elif (
                            event.key == pygame.K_LEFT
                            and player.action == Action.WALKING
                        ):
                            player.command_walk_left()
                        elif (
                            event.key == pygame.K_RIGHT
                            and player.action == Action.WALKING
                        ):
                            player.command_walk_right()
                        elif (
                            event.key == pygame.K_RIGHT
                            and player.action == Action.DIGGING
                        ):  # Digging to RIGHT.
                            player.command_start_digging(tunnels, waypoint_net)
                            tunnels[-1].direction = TunnelDirection.FLAT
                            player.direction = Direction.RIGHT
                            player.x_speed = SPEED_DIGGING
                            player.y_speed = 0
                        elif (
                            event.key == pygame.K_LEFT
                            and player.action == Action.DIGGING
                        ):  # Digging to LEFT.
                            player.command_start_digging(tunnels, waypoint_net)
                            tunnels[-1].direction = TunnelDirection.FLAT
                            player.direction = Direction.LEFT
                            player.x_speed = -SPEED_DIGGING
                            player.y_speed = 0
                        elif (
                            event.key == pygame.K_UP and player.action == Action.DIGGING
                        ):
                            player.command_start_digging(tunnels, waypoint_net)
                            if (
                                player.direction == Direction.RIGHT
                            ):  # Digging to RIGHT UP.
                                player.x_speed = SPEED_DIGGING
                                tunnels[-1].direction = TunnelDirection.RIGHTUP
                            else:  # Digging to LEFT UP.
                                player.x_speed = -SPEED_DIGGING
                                tunnels[-1].direction = TunnelDirection.LEFTUP
                            player.y_speed = -SPEED_DIGGING / 2
                        elif (
                            event.key == pygame.K_DOWN
                            and player.action == Action.DIGGING
                        ):
                            player.command_start_digging(tunnels, waypoint_net)
                            if (
                                player.direction == Direction.RIGHT
                            ):  # Digging to RIGHT DOWN.
                                player.x_speed = SPEED_DIGGING
                                tunnels[-1].direction = TunnelDirection.RIGHTDOWN
                            else:  # Digging to LEFT DOWN.
                                player.x_speed = -SPEED_DIGGING
                                tunnels[-1].direction = TunnelDirection.LEFTDOWN
                            player.y_speed = SPEED_DIGGING
                        elif (
                            event.key == pygame.K_UP and player.action == Action.WALKING
                        ):
                            if player.direction == Direction.LEFT:
                                player.command_jump_left()
                            else:
                                player.command_jump_right()
                    if event.type == pygame.KEYUP:
                        if (
                            event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT
                        ) and player.action == Action.WALKING:
                            player.command_stop()
                        if (
                            event.key == pygame.K_LEFT
                            and player.action == Action.DIGGING
                        ):
                            player.x_speed = 0
                            player.y_speed = 0
                        if (
                            event.key == pygame.K_RIGHT
                            and player.action == Action.DIGGING
                        ):
                            player.x_speed = 0
                            player.y_speed = 0
                        if event.key == pygame.K_UP and player.action == Action.DIGGING:
                            player.x_speed = 0
                            player.y_speed = 0
                        if (
                            event.key == pygame.K_DOWN
                            and player.action == Action.DIGGING
                        ):
                            player.x_speed = 0
                            player.y_speed = 0

            # No action when debug mode in set.
            if debug_mode:
                break

            if type(player) == AIPlayer:
                # Does the AI have a patrol task?
                if ai_timer < AI_TIMER and len(player.patrol_between_tunnels) > 1:
                    path = weightless_breadth_first_search(
                        waypoint_net,
                        player.last_visited_tunnel,
                        player.patrol_between_tunnels[0],
                    )
                    if len(path) > 0:
                        next_node = path[1]
                        if tunnels[next_node].end_x > player.x:
                            if (
                                player.x_speed == 0
                                and tunnels[player.last_visited_tunnel].end_y
                                > tunnels[next_node].end_y
                                and not player.is_there_solid_material(screen, 10, -1)
                            ):
                                player.command_jump_right()
                            player.command_walk_right()
                        elif tunnels[next_node].end_x < player.x:
                            if (
                                player.x_speed == 0
                                and tunnels[player.last_visited_tunnel].end_y
                                > tunnels[next_node].end_y
                                and not player.is_there_solid_material(screen, -10, -1)
                            ):
                                player.command_jump_left()
                            player.command_walk_left()
                        else:
                            player.command_stop()
                            player.last_visited_tunnel = next_node
                            if (
                                player.last_visited_tunnel
                                == player.patrol_between_tunnels[0]
                            ):
                                player.patrol_between_tunnels = (
                                    player.patrol_between_tunnels[1:]
                                    + [player.patrol_between_tunnels[0]]
                                )

            # Apply speed if there are no walls.
            if player.x_speed > 0:
                if player.is_there_solid_material(
                    screen, 7, 0
                ) and player.is_there_solid_material(screen, 7, -20):
                    player.x_speed = 0
                else:
                    player.x += player.x_speed
            elif player.x_speed < 0:
                if player.is_there_solid_material(
                    screen, -7, 0
                ) and player.is_there_solid_material(screen, -7, -20):
                    player.x_speed = 0
                else:
                    player.x += player.x_speed
            player.y += player.y_speed
            # The player should not leave the screen.
            if player.x < 10:
                player.x = 10
            elif player.x >= WINDOW_SIZE[0] - 10:
                player.x = WINDOW_SIZE[0] - 11
            if player.y < 0:
                player.y = 0
            elif player.y >= WINDOW_SIZE[1]:
                player.y = WINDOW_SIZE[1] - 1
            # Is the player falling?
            if player.action == Action.FALLING:
                # Gravitation.
                if player.y_speed < 10:
                    player.y_speed += 0.5
                # Hit the ground?
                if player.y_speed > 0 and player.is_there_solid_material(screen, 0, 1):
                    player.x_speed = 0
                    player.y_speed = 0
                    player.action = Action.WALKING
                # Hit the ceiling with the head?
                if player.y_speed < 0 and (
                    player.is_there_solid_material(screen, -5, -PLAYER_HGT)
                    or player.is_there_solid_material(screen, 5, -PLAYER_HGT)
                ):
                    player.x_speed = 0
                    player.y_speed = 0
            if player.action == Action.WALKING:
                a = False
                if player.x_speed != 0:
                    if not player.is_there_solid_material(screen, 0, 1):
                        player.y += 1
                        if not player.is_there_solid_material(screen, 0, 1):
                            player.y += 1
                            if not player.is_there_solid_material(screen, 0, 1):
                                player.y += 1
                                if not player.is_there_solid_material(screen, 0, 1):
                                    player.action = Action.FALLING
                        a = True
                    while (
                        player.is_there_solid_material(screen, -5, -2)
                        or player.is_there_solid_material(screen, 5, -2)
                    ) and a == False:
                        player.y -= 1
            if player.action == Action.DIGGING:
                # Move the end of the latest tunnel segment to the player's position.
                tunnels[-1].end_x = player.x
                tunnels[-1].end_y = player.y
                # The player should fall down while digging when there is no earth below.
                if not player.is_there_solid_material(
                    screen, 0, 3
                ) and not player.is_there_solid_material(screen, 0, 1):
                    player.action = Action.FALLING

        # Drawing.
        pygame.draw.rect(screen, (240, 240, 250), (0, 0, WINDOW_SIZE[0], 100))
        pygame.draw.rect(screen, (0, 0, 0), (0, 99, WINDOW_SIZE[0], 100))
        pygame.draw.rect(screen, EARTH_COLOR, (0, 100, WINDOW_SIZE[0], 700))
        for tunnel in tunnels:  # Using the design pattern "Iterator".
            tunnel.draw(screen)
        if debug_mode:
            i = 0
            for tunnel in tunnels:  # Using the design pattern "Iterator".
                net = str(waypoint_net[str(i)])
                screen.blit(
                    tiny_font.render(str(i) + net, True, (255, 255, 255)),
                    (tunnel.end_x, tunnel.end_y),
                )
                i += 1
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (BUTTON_DEBUG_X, BUTTON_DEBUG_Y, BUTTON_DEBUG_WDT, BUTTON_DEBUG_HGT),
        )
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                BUTTON_DEBUG_X + 1,
                BUTTON_DEBUG_Y + 1,
                BUTTON_DEBUG_WDT - 2,
                BUTTON_DEBUG_HGT - 2,
            ),
        )
        screen.blit(text, (BUTTON_DEBUG_X + 10, BUTTON_DEBUG_Y + 10))
        screen.blit(text2, (BUTTON_DEBUG_X + 10, BUTTON_DEBUG_Y + 50))
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (BUTTON_RESET_X, BUTTON_RESET_Y, BUTTON_RESET_WDT, BUTTON_RESET_HGT),
        )
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                BUTTON_RESET_X + 1,
                BUTTON_RESET_Y + 1,
                BUTTON_RESET_WDT - 2,
                BUTTON_RESET_HGT - 2,
            ),
        )
        screen.blit(text_reset, (BUTTON_RESET_X + 10, BUTTON_RESET_Y + 10))
        for flag in flags:  # Using the design pattern "Iterator".
            flag.draw(screen)
        for player in players:  # Using the design pattern "Iterator".
            player.draw(screen)

        # Update the display.
        pygame.display.update()


def weightless_breadth_first_search(graph, start, end) -> []:
    """Finds the a list of nodes between two nodes. The function does not care about the distance between nodes (weights)."""
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


if __name__ == "__main__":
    main()
