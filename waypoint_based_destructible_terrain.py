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

# Variables that change over time.
pygame.init()
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

while running:
	# Limit the game to 36 FPS.
	clock.tick(36)

	# Quitting.
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	# Apply speed.
	player1.x += player1.x_speed
	player1.y += player1.y_speed

	# Is the player falling?
	if player1.action == Action.FALLING:
		# Gravitation.
		if player1.y_speed < 10:
			player1.y_speed += 1
		# Hit the ground?
		if player1.y_speed > 0 and tuple(pygame.Surface.get_at(screen, (player1.x, player1.y+1))[:3]) not in [SKY_COLOR, TUNNEL_COLOR]:
			player1.y_speed = 0
			player1.action = Action.WALKING
		
	# Keyboard input.
	if event.type==pygame.KEYDOWN:
		if event.key==pygame.K_LEFT:
			player1.x_speed = -SPEED_WALKING
		if event.key==pygame.K_RIGHT:
			player1.x_speed = SPEED_WALKING
		if event.key==pygame.K_UP and player1.action == Action.WALKING:
			player1.action = Action.FALLING
			player1.y_speed = -10
	if event.type==pygame.KEYUP:
		if event.key==pygame.K_LEFT:
			player1.x_speed = 0
		if event.key==pygame.K_RIGHT:
			player1.x_speed = 0

	# Draw earth.
	pygame.draw.rect(screen, EARTH_COLOR, (0, 200, WINDOW_SIZE[0], 600))
	
	# Draw the sky.
	pygame.draw.rect(screen, SKY_COLOR, (0, 0, WINDOW_SIZE[0], 200))
	
	# Draw player.
	pygame.draw.polygon(screen, (255, 0, 0), ((player1.x, player1.y), (player1.x-5, player1.y-20), (player1.x+5, player1.y-20)), 0)

	# Update the display.
	pygame.display.update()

pygame.quit()
