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
SPEED_WALKING = 2
SPEED_DIGGING = 1
BUTTON_X = 10
BUTTON_Y = 10
BUTTON_WDT = 270
BUTTON_HGT = 40

# Variables that change over time.
pygame.init()
pygame.display.set_caption('waypoint based destructible terrain')
screen = pygame.display.set_mode(WINDOW_SIZE)
running = True
clock = pygame.time.Clock()


class Action(Enum):
    FALLING = auto()
    WALKING = auto()
    DIGGING = auto()


class Player:
    action: Action
    x: float
    y: float
    x_speed: float
    y_speed: float


player1 = Player()
player1.action = Action.WALKING
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
            player1.y_speed = 0
            player1.action = Action.WALKING

    # Keyboard input.
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player1.x_speed = -SPEED_WALKING
            if player1.action == Action.DIGGING:
                player1.x_speed = -SPEED_DIGGING
        elif event.key == pygame.K_RIGHT:
            player1.x_speed = SPEED_WALKING
            if player1.action == Action.DIGGING:
                player1.x_speed = SPEED_DIGGING
        elif event.key == pygame.K_UP and player1.action == Action.WALKING:
            player1.action = Action.FALLING
            player1.y_speed = -10
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player1.x_speed = 0
        elif event.key == pygame.K_RIGHT:
            player1.x_speed = 0

    # Draw earth.
    pygame.draw.rect(screen, EARTH_COLOR, (0, 200, WINDOW_SIZE[0], 600))

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
