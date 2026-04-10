from math import sqrt
from typing import Final
import arcade

from constants import *
from textures import *
from entities import *
from map import Map, GridCell, NavMeshNode, load_map_from_file


class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    map: Map

    player: Player
    player_sprite_list: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    crystals: Final[arcade.SpriteList[Entity]]

    monsters: Final[arcade.SpriteList[Entity]]

    grounds: arcade.SpriteList[arcade.Sprite]
    walls: arcade.SpriteList[arcade.Sprite]

    holes: arcade.SpriteList[arcade.Sprite]

    switches: arcade.SpriteList[arcade.Sprite]
    gates: arcade.SpriteList[arcade.Sprite]


    weapons: list[Weapon]
    current_weapon: Weapon

    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]

    pressed_keys: list[bool]

    show_hitboxes: bool
    show_navmesh: bool

    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.map = load_map_from_file("maps/map2.txt")
        self.map.initialize_navmesh(1)

        # Setup our game
        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

        self.player_sprite_list = arcade.SpriteList()
        self.crystals = arcade.SpriteList()
        self.monsters = arcade.SpriteList()
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.holes = arcade.SpriteList(use_spatial_hash=True)
        self.switches = arcade.SpriteList(use_spatial_hash=True)
        self.gates = arcade.SpriteList(use_spatial_hash=True)


        self.pressed_keys = [False, False, False, False]

        self.show_hitboxes = False
        self.show_navmesh = False


        for cell_j in range(self.map.height):
            for cell_i in range(self.map.width):
                cell_x: int = self.map.i_to_x(cell_i)
                cell_y: int = self.map.j_to_y(cell_j)
                cell = self.map.get(cell_i, cell_j)
                match cell:
                    case GridCell.GRASS:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                    case GridCell.BUSH:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        self.walls.append(arcade.Sprite(
                            TEXTURE_BUSH,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                    case GridCell.CRYSTAL:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        self.crystals.append(Entity(cell_x, cell_y, arcade.Vec2
(0, 1), 0, CRYSTAL_ANIMATION))
                    case GridCell.VERTICAL_SPINNER:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))

                        self.monsters.append(Spinner(cell_x, cell_y, arcade.Vec2
(0, 1), self.map))
                    case GridCell.HORIZONTAL_SPINNER:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        self.monsters.append(Spinner(cell_x, cell_y, arcade.Vec2
(1, 0), self.map))
                    case GridCell.HOLE:
                        self.holes.append(arcade.Sprite(
                            TEXTURE_HOLE,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                    case GridCell.BAT:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        self.monsters.append(Bat(cell_x, cell_y))
                    case GridCell.BLOB:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        self.monsters.append(Blob(cell_x, cell_y, self.map))

                    case GridCell.SWITCH:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        # switches are added later

                    case GridCell.GATE:
                        self.grounds.append(arcade.Sprite(
                            TEXTURE_GRASS,
                            scale=SCALE, center_x=cell_x, center_y=cell_y
                        ))
                        # gates are added later

        switch_dict: dict
        for switch in self.map.switches:
            center_x: int = switch["x"] * TILE_SIZE + TILE_SIZE//2
            center_y: int = switch["y"] * TILE_SIZE - TILE_SIZE//2
            state: bool
            if "state" in switch:
                state = switch["state"]
            else:
                state: bool = False
            id: str = switch["id"]

            self.switches.append(Switch(center_x, center_y, state, id))

        for gate in self.map.gates:
            center_x: int = gate["x"] * TILE_SIZE + TILE_SIZE//2
            center_y: int = gate["y"] * TILE_SIZE - TILE_SIZE//2
            open_condition: list[dict] = gate["open_if"]

            self.gates.append(Gate(center_x, center_y, open_condition, self.switches))

        self.player = Player(self.map.i_to_x(self.map.player_start_x), self.map.i_to_x(self.map.player_start_y))
        self.player_sprite_list.append(self.player)

        self.weapons = []
        self.weapons.append(Boomerang(self.player))
        self.weapons.append(Sword(self.player))
        self.current_weapon = self.weapons[0]

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

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
            self.holes.draw()
            self.switches.draw()
            self.gates.draw()
            self.crystals.draw()
            self.monsters.draw()
            if type(self.current_weapon) != Sword or self.current_weapon.state == 0:
                self.player_sprite_list.draw()
            if self.current_weapon.state != 0:
                arcade.draw_sprite(self.current_weapon)

            if self.show_navmesh:
                nodes: list[NavMeshNode] = list(self.map.navmesh.nodes)
                for node in nodes:
                    pos: arcade.Vec2 = arcade.Vec2(self.map.navmesh.nodes[node]["x"], self.map.navmesh.nodes[node]["y"])
                    arcade.draw_circle_filled(pos.x, pos.y, 2, arcade.color.BLACK)
                    for neighbor in self.map.navmesh.neighbors(node):
                        arcade.draw_line(pos.x, pos.y, self.map.navmesh.nodes[neighbor]["x"], self.map.navmesh.nodes[neighbor]["y"], arcade.color.BLACK, 2)
                for monster in self.monsters:
                    if type(monster) == Blob:
                        temp_target = monster.path_to_target[monster.path_index]
                        last_target = monster.path_to_target[-1]
                        arcade.draw_rect_filled(arcade.rect.XYWH(temp_target.x, temp_target.y, 16, 16), (100, 100, 255, 75))
                        arcade.draw_rect_filled(arcade.rect.XYWH(last_target.x, last_target.y, 16, 16), (100, 255, 100, 75))
                        arcade.draw_line_strip(monster.path_to_target, arcade.color.RED, 2)
                        #arcade.draw_rect_outline(arcade.rect.XYWH(grid_to_pixels(pixels_to_grid(monster.target.x)), self.world_height - (pixels_to_grid(monster.target.y)), TILE_SIZE, TILE_SIZE), arcade.color.WHITE)
            if self.show_hitboxes:
                self.player_sprite_list.draw_hit_boxes()
                self.crystals.draw_hit_boxes()
                self.walls.draw_hit_boxes()
                self.holes.draw_hit_boxes()
                self.monsters.draw_hit_boxes()
                self.current_weapon.draw_hit_box()
                monster: Entity

                for monster in self.monsters:
                    arcade.draw_rect_outline(arcade.rect.LRBT(monster.start_boundary_x, monster.end_boundary_x, monster.end_boundary_y, monster.start_boundary_y), arcade.color.WHITE)
                    # draw direction
                    arcade.draw_line(monster.center_x, monster.center_y, monster.center_x + 50 * monster.direction.x, monster.center_y + 50 * monster.direction.y, arcade.color.BABY_BLUE, 2)
                    if type(monster) == Bat or type(monster) == Blob:
                        arcade.draw_rect_filled(arcade.rect.XYWH(monster.target.x, monster.target.y, 16, 16), (255, 100, 100, 75))
        with self.gui_camera.activate():
            cursor_index: int = 20
            score_counter = arcade.Text(str(self.player.crystal_count),
                        cursor_index,
                        self.window.height - 30,
                        arcade.color.WHITE_SMOKE,
                        25,
                        font_name="Kenney Rocket")
            score_counter.draw()
            cursor_index += score_counter.content_width + 40

            for i in range(len(self.weapons)):
                if type(self.weapons[i]) == type(self.current_weapon):
                    color = arcade.color.WHITE_SMOKE
                else:
                    color = arcade.color.GRAY

                weapon_text = arcade.Text(self.weapons[i].display_name,
                        cursor_index,
                        self.window.height-30,
                        color,
                        25,
                        font_name="Kenney Mini")
                weapon_text.draw()
                cursor_index += weapon_text.content_width + 20


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
            case arcade.key.R:
                if self.current_weapon.state == 0:
                    current_weapon_index = self.weapons.index(self.current_weapon)
                    current_weapon_index = (current_weapon_index + 1) % len(self.weapons)
                    self.current_weapon = self.weapons[current_weapon_index]
            case arcade.key.SPACE:
                if self.current_weapon.state == 0:
                    self.current_weapon.state = 1
            case arcade.key.ESCAPE:
                game_view = GameView()
                self.window.show_view(game_view)

            case arcade.key.H:
                self.show_hitboxes = not self.show_hitboxes
            case arcade.key.N:
                self.show_navmesh = not self.show_navmesh

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
        self.current_weapon.move()
        for switch in self.switches:
            switch.tick()
        for gate in self.gates:
            gate.tick()
        for crystal in self.crystals:
            crystal.move()
        for monster in self.monsters:
            if type(monster) == Blob:
                if arcade.has_line_of_sight(monster.center, self.player.center, self.walls) and (monster.center - self.player.center).length() <= 5*TILE_SIZE:
                    monster.can_see_player = True
                    monster.last_seen_player = self.player.center

            monster.move()


        for sprite in arcade.check_for_collision_with_list(self.player, self.crystals):
            sprite.remove_from_sprite_lists()
            self.player.crystal_count += 1
        if self.current_weapon.state != 0:
            for sprite in arcade.check_for_collision_with_list(self.current_weapon, self.monsters):
                sprite.remove_from_sprite_lists()
                self.current_weapon.hit_something = True
            if arcade.check_for_collision_with_list(self.current_weapon, self.walls):
                self.current_weapon.hit_something = True
            if arcade.check_for_collision_with_list(self.current_weapon, self.switches):
                arcade.check_for_collision_with_list(self.current_weapon, self.switches)[0].toggle()
                self.current_weapon.hit_something = True

        if arcade.check_for_collision_with_list(self.player, self.monsters):
            game_view = GameView()
            self.window.show_view(game_view)
        if arcade.get_closest_sprite(self.player, self.holes) is not None:
            if arcade.get_closest_sprite(self.player, self.holes)[1] <= 16:
                game_view = GameView()
                self.window.show_view(game_view)
        if type(self.current_weapon) == Sword and self.current_weapon.state != 0:
            for sprite in arcade.check_for_collision_with_list(self.current_weapon, self.crystals):
                sprite.remove_from_sprite_lists()
                self.player.crystal_count += 1

        self.physics_engine.update()
        new_camera_x = self.player.center_x
        new_camera_y = self.player.center_y
        if new_camera_x < self.camera.viewport_width/2 or self.camera.viewport_width > self.world_width:
            new_camera_x = self.camera.viewport_width/2
        if new_camera_x > self.world_width - self.camera.viewport_width/2:
            new_camera_x = self.world_width - self.camera.viewport_width/2

        if new_camera_y < self.camera.viewport_height/2 or self.camera.viewport_height > self.world_height:
            new_camera_y = self.camera.viewport_height/2
        elif new_camera_y > self.world_height - self.camera.viewport_height/2:
            new_camera_y = self.world_height - self.camera.viewport_height/2


        self.camera.position = (new_camera_x, new_camera_y)
