"""
Project name: waypoint_based_destructible_terrain
Author: Armin Schäfer
Requirements: ```pip install pygame```
"""

# Standard libraries.
import math
from enum import Enum, auto

# Third party libraries.
import pygame

# Constants.
WINDOW_SIZE = (1000, 800)
SKY_COLOR = (215, 212, 255)
EARTH_COLOR = (200, 130, 110)
TUNNEL_COLOR = (100, 30, 10)
SPEED_WALKING = 3
SPEED_DIGGING = 1
SPEED_JUMPING = 8
BUTTON_X = 10
BUTTON_Y = 10
BUTTON_WDT = 270
BUTTON_HGT = 40
TUNNEL_HGT = 40
PLAYER_HGT = 20

# Variables that change over time.
pygame.init()
pygame.display.set_caption("waypoint based destructible terrain")
screen = pygame.display.set_mode(WINDOW_SIZE)
running = True
clock = pygame.time.Clock()
tunnels = []


class DirectionDigging(Enum):
    LEFT_UP = auto()
    LEFT = auto()
    LEFT_DOWN = auto()
    RIGHT_DOWN = auto()
    RIGHT = auto()
    RIGHT_UP = auto()


class Action(Enum):
    FALLING = auto()
    WALKING = auto()
    DIGGING = auto()


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()


class Player:
    action: Action
    direction: Direction
    x: float
    y: float
    x_speed: float
    y_speed: float

    def command_jump_left(self):
        player1.direction = Direction.LEFT
        player1.action = Action.FALLING
        player1.x_speed = -SPEED_WALKING
        player1.y_speed = -SPEED_JUMPING

    def command_jump_right(self):
        player1.direction = Direction.RIGHT
        player1.action = Action.FALLING
        player1.x_speed = SPEED_WALKING
        player1.y_speed = -SPEED_JUMPING

    def command_walk_left(self):
        player1.direction = Direction.LEFT
        player1.x_speed = -SPEED_WALKING

    def command_walk_right(self):
        player1.direction = Direction.RIGHT
        player1.x_speed = SPEED_WALKING

    def command_stop(self):
        player1.x_speed = 0


class Tunnel:
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    # direction: DirectionDigging

    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y


tunnels.append(Tunnel(200, 200, 400, 400))
tunnels.append(Tunnel(400, 200, 200, 400))

player1 = Player()
player1.action = Action.WALKING
player1.direction = Direction.LEFT
player1.x = 100
player1.y = 200
player1.x_speed = 0
player1.y_speed = 0
debug_mode = False
smallfont = pygame.font.SysFont("Corbel", 35)
text = smallfont.render("Turn on debug mode", True, (0, 0, 0))

while running:
    # Limit the game to 36 FPS.
    clock.tick(36)

    # Mouse events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if (
                BUTTON_X <= mouse[0] <= BUTTON_X + BUTTON_WDT
                and BUTTON_Y <= mouse[1] <= BUTTON_Y + BUTTON_HGT
            ):
                debug_mode = not debug_mode
                if debug_mode:
                    text = smallfont.render("Turn off debug mode", True, (0, 0, 0))
                else:
                    text = smallfont.render("Turn on debug mode", True, (0, 0, 0))

    # Apply speed.
    player1.x += player1.x_speed
    player1.y += player1.y_speed
    # The player should not leave the screen.
    if player1.x < 0:
        player1.x = 0
    elif player1.x >= WINDOW_SIZE[0]:
        player1.x = WINDOW_SIZE[0] - 1
    if player1.y < 0:
        player1.y = 0
    elif player1.y >= WINDOW_SIZE[1]:
        player1.y = WINDOW_SIZE[1] - 1

    # Is the player falling?
    if player1.action == Action.FALLING:
        # Gravitation.
        if player1.y_speed < 10:
            player1.y_speed += 1
        # Hit the ground?
        if player1.y_speed > 0 and tuple(
            pygame.Surface.get_at(screen, (player1.x, player1.y + 1))[:3]
        ) not in [SKY_COLOR, TUNNEL_COLOR]:
            player1.x_speed = 0
            player1.y_speed = 0
            player1.action = Action.WALKING
        # Hit the ceiling with the head?
        if player1.y_speed < 0 and (
            tuple(
                pygame.Surface.get_at(screen, (player1.x - 5, player1.y - PLAYER_HGT))[
                    :3
                ]
            )
            not in [SKY_COLOR, TUNNEL_COLOR]
            or tuple(
                pygame.Surface.get_at(screen, (player1.x + 5, player1.y - PLAYER_HGT))[
                    :3
                ]
            )
            not in [SKY_COLOR, TUNNEL_COLOR]
        ):
            player1.x_speed = 0
            player1.y_speed = 0

    if player1.action == Action.WALKING:
        if player1.x_speed != 0:
            """
            # Player walking against wall? TODO: Not working.
            if player1.x_speed > 0 and tuple(
                pygame.Surface.get_at(screen, (player1.x + 6, player1.y - PLAYER_HGT / 2))[
                    :3
                ]
            ) not in [SKY_COLOR, TUNNEL_COLOR]:
                player1.x_speed = 0
            if player1.x_speed < 0 and tuple(
                pygame.Surface.get_at(screen, (player1.x - 6, player1.y - PLAYER_HGT / 2))[
                    :3
                ]
            ) not in [SKY_COLOR, TUNNEL_COLOR]:
                player1.x_speed = 0
            """
            # Is the player walking uphill or downhill?
            while tuple(
                pygame.Surface.get_at(screen, (player1.x, player1.y + 1))[:3]
            ) in [
                SKY_COLOR,
                TUNNEL_COLOR,
            ]:
                player1.y += 1
            while tuple(
                pygame.Surface.get_at(screen, (player1.x, player1.y))[:3]
            ) not in [
                SKY_COLOR,
                TUNNEL_COLOR,
            ]:
                player1.y -= 1

    # Keyboard input.
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT and player1.action == Action.DIGGING:
            player1.x_speed = -SPEED_DIGGING
        if event.key == pygame.K_LEFT and player1.action == Action.WALKING:
            player1.command_walk_left()
        if event.key == pygame.K_RIGHT and player1.action == Action.DIGGING:
            player1.x_speed = SPEED_DIGGING
        if event.key == pygame.K_RIGHT and player1.action == Action.WALKING:
            player1.command_walk_right()
        elif event.key == pygame.K_UP and player1.action == Action.WALKING:
            if player1.direction == Direction.LEFT:
                player1.command_jump_left()
            else:
                player1.command_jump_right()
    if event.type == pygame.KEYUP:
        if (
            event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT
        ) and player1.action == Action.WALKING:
            player1.command_stop()

    # Draw earth.
    pygame.draw.rect(screen, EARTH_COLOR, (0, 200, WINDOW_SIZE[0], 600))

    # Draw tunnels.
    for tunnel in tunnels:
        pygame.draw.line(
            screen,
            TUNNEL_COLOR,
            (tunnel.start_x, tunnel.start_y - TUNNEL_HGT / 2),
            (tunnel.end_x, tunnel.end_y - TUNNEL_HGT / 2),
            width=TUNNEL_HGT,
        )
        pygame.draw.circle(
            screen,
            TUNNEL_COLOR,
            (tunnel.end_x, tunnel.end_y - TUNNEL_HGT / 2),
            TUNNEL_HGT / 2,
        )
        if debug_mode:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (tunnel.start_x, tunnel.start_y),
                3,
            )
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (tunnel.end_x, tunnel.end_y),
                3,
            )

    # Draw the sky.
    pygame.draw.rect(screen, SKY_COLOR, (0, 0, WINDOW_SIZE[0], 200))
    
    # Button for debug mode.
    pygame.draw.rect(screen, (0, 0, 0), (BUTTON_X, BUTTON_Y, BUTTON_WDT, BUTTON_HGT))
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (BUTTON_X + 1, BUTTON_Y + 1, BUTTON_WDT - 2, BUTTON_HGT - 2),
    )
    screen.blit(text, (BUTTON_X + 10, BUTTON_Y + 10))

    # Draw player.
    player_color = (255, 0, 0)
    if player1.action == Action.DIGGING:
        player_color = (255, 255, 0)
    pygame.draw.polygon(
        screen,
        player_color,
        (
            (player1.x, player1.y),
            (player1.x - 5, player1.y - 20),
            (player1.x + 5, player1.y - 20),
        ),
        0,
    )

    # Update the display.
    pygame.display.update()

pygame.quit()
