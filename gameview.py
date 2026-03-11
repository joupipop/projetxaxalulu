from math import sqrt
from typing import Final
import arcade

from constants import *
from textures import *
from entities import *

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    player: Player
    player_sprite_list: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    grounds: arcade.SpriteList[arcade.Sprite]
    walls: arcade.SpriteList[arcade.Sprite]

    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]

    pressed_keys: list[bool]

    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.world_width = 40 * TILE_SIZE
        self.world_height = 20 * TILE_SIZE

        self.player = Player(grid_to_pixels(2), grid_to_pixels(2))
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player)

        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)

        self.pressed_keys = [False, False, False, False]

        """create ground"""
        for x in range(0, 40):
            for y in range(0, 20):
                self.grounds.append(arcade.Sprite(
                    TEXTURE_GRASS,
                    scale=SCALE, center_x=grid_to_pixels(x), center_y=grid_to_pixels(y)
                ))

        """add bushes"""
        coord_list: list[tuple[int, int]] = [(3, 6), (7, 2), (2, 10), (3, 8)]
        for coord in coord_list:
            self.walls.append(arcade.Sprite(
                TEXTURE_BUSH,
                scale=SCALE, center_x=grid_to_pixels(coord[0]), center_y=grid_to_pixels(coord[1])
            ))

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()

    def on_show_view(self) -> None:
        """Called automatically by 'window.show_view(game_view)' in main.py."""
        # When we show the view, adjust the window's size to our world size.
        # If the world size is smaller than the maximum window size, we should
        # limit the size of the window.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        with self.camera.activate():
            self.grounds.draw()
            self.walls.draw()
            self.player_sprite_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match symbol:
            case arcade.key.UP | arcade.key.W:
                self.pressed_keys[0] = True
            case arcade.key.DOWN | arcade.key.S:
                self.pressed_keys[1] = True
            case arcade.key.LEFT | arcade.key.A:
                self.pressed_keys[2] = True
            case arcade.key.RIGHT | arcade.key.D:
                self.pressed_keys[3] = True

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match symbol:
            case arcade.key.UP | arcade.key.W:
                self.pressed_keys[0] = False
            case arcade.key.DOWN | arcade.key.S:
                self.pressed_keys[1] = False
            case arcade.key.LEFT | arcade.key.A:
                self.pressed_keys[2] = False
            case arcade.key.RIGHT | arcade.key.D:
                self.pressed_keys[3] = False

    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.player.change_x = (self.pressed_keys[3] - self.pressed_keys[2]) * self.player.speed
        self.player.change_y = (self.pressed_keys[0] - self.pressed_keys[1]) * self.player.speed

        self.player.move()

        self.physics_engine.update()
        self.camera.position = self.player.position
