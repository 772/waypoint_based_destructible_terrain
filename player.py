from waypoint_based_destructible_terrain import *
from constants import *
from enum import Enum, auto

# Third-party libraries.
import pygame


class Action(Enum):
    """Used by the class Player. There are three different actions a player can have."""

    FALLING = auto()
    WALKING = auto()
    DIGGING = auto()


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
    color: tuple
    x_speed: float
    y_speed: float
    last_visited_tunnels: list

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
                self.last_visited_tunnels = self.find_two_nearby_tunnels(game_state)
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

    def get_nearest_tunnel(self, game_state) -> list:
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

    def find_two_nearby_tunnels(self, game_state):
        """This function will give you the two tunnels a player is inbetween with.
        This is done by linear algebra: Is a point on a line?"""
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
                # The following six lines are very hacky because of weird waypoint positions in diagonal tunnels.
                y_offset = 8 if x2 < x1 else 6 # Also, diagonal tunnels to the left have a different offset than tunnels to the right.
                a = math.fabs(x - x1)
                b = math.fabs((y - y_offset) - y1)
                c = math.fabs(x - x2)
                d = math.fabs((y - y_offset) - y2)
                if (a == b or a == (b - 2)) and (c == d or c == (d - 2)):
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

        # If all "tunnel ends" are only on one side, we found nothing.
        if len(hits) < 2:
            return []

        # Check if the "tunnel ends" are even connected in the waypoint_net.
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
            # The player should not fall directly when walking downhill.
            # This part of the code could also be done via a for loop.
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

    patrol_between_tunnels: list
    current_path: list

    def update(self, game_state):
        """Update the patrol path in AIs."""
        if len(self.patrol_between_tunnels) < 2 or self.action != Action.WALKING:
            return  # AI has no patrol task.
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
