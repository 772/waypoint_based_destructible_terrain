import math

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
