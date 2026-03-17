from math import sqrt
from typing import Final
import arcade

from constants import *
from textures import *
from entities import *
from map import Map, GridCell, load_map_from_file, grid_to_pixels



class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    player: Player
    player_sprite_list: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    crystals: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    spinners: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

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

        map: Map = load_map_from_file("maps/map1.txt")

        # Setup our game
        self.world_width = map.width * TILE_SIZE
        self.world_height = map.height * TILE_SIZE

        self.player_sprite_list = arcade.SpriteList()
        self.crystals = arcade.SpriteList()
        self.spinners = arcade.SpriteList()
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)

        self.pressed_keys = [False, False, False, False]

        for cell_y in range(map.height):
            for cell_x in range(map.width):
                cell = map.get(cell_x, cell_y)
                match cell:
                    case GridCell.GRASS:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=grid_to_pixels(cell_x), center_y=grid_to_pixels(cell_y)
                        ))
                    case GridCell.BUSH:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=grid_to_pixels(cell_x), center_y=grid_to_pixels(cell_y)
                        ))
                        self.walls.append(arcade.Sprite(
                            TEXTURE_BUSH,
                            scale=SCALE, center_x=grid_to_pixels(cell_x), center_y=grid_to_pixels(cell_y)
                        ))
                    case GridCell.CRYSTAL:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=grid_to_pixels(cell_x), center_y=grid_to_pixels(cell_y)
                        ))
                        self.crystals.append(Entity(grid_to_pixels(cell_x), grid_to_pixels(cell_y), Vector2D(0, -1), 0, CRYSTAL_ANIMATION))
                    case GridCell.VERTICAL_SPINNER:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=grid_to_pixels(cell_x), center_y=grid_to_pixels(cell_y)
                        ))

                        self.spinners.append(Spinner(grid_to_pixels(cell_x), grid_to_pixels(cell_y), Vector2D(0, 1), map))
                    case GridCell.HORIZONTAL_SPINNER:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=grid_to_pixels(cell_x), center_y=grid_to_pixels(cell_y)
                        ))
                        self.spinners.append(Spinner(grid_to_pixels(cell_x), grid_to_pixels(cell_y), Vector2D(1, 0), map))

        self.player = Player(grid_to_pixels(map.player_start_x), grid_to_pixels(map.player_start_y))
        self.player_sprite_list.append(self.player)            # self.player_sprite_list.draw_hit_boxes()
            # self.crystals.draw_hit_boxes()
            # self.walls.draw_hit_boxes()

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
            self.crystals.draw()
            self.spinners.draw()
            self.player_sprite_list.draw()
            #self.player_sprite_list.draw_hit_boxes()
            #self.crystals.draw_hit_boxes()
            #self.walls.draw_hit_boxes()



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
            case arcade.key.ESCAPE:
                game_view = GameView()
                self.window.show_view(game_view)

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

        self.player.input(self.pressed_keys)
        self.player.move()
        for crystal in self.crystals:
            crystal.move()
        for spinner in self.spinners:
            spinner.move()

        for sprite in arcade.check_for_collision_with_list(self.player, self.crystals):
            sprite.remove_from_sprite_lists()

        if arcade.check_for_collision_with_list(self.player, self.spinners):
            game_view = GameView()
            self.window.show_view(game_view)
            print("dead")


        self.physics_engine.update()
        new_camera_position: list[int | float] = list(self.camera.position)
        if self.player.position[0] > self.window.width/2-2:
            new_camera_position[0] = self.player.position[0]
        if self.player.position[1] > self.window.height/2-5:
            new_camera_position[1] = self.player.position[1]

        self.camera.position = tuple(new_camera_position)
