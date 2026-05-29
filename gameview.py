from arcade import Sound
from typing import Final, assert_never
import time
import pyglet.media

from constants import *
from textures import *
from entities import *
from map import Map, GridCell, NavMeshNode, load_map_from_file, InvalidMapFileException


class GameView(arcade.View):
    """Main in-game view."""

    __world_width: Final[int]
    __world_height: Final[int]

    __map: Map
    __player: Player
    __players: arcade.SpriteList[arcade.TextureAnimationSprite]

    __collectables: arcade.SpriteList[Entity]
    _remaining_crystals: int

    __sword_item: arcade.SpriteList[Entity]
    __boomerang_item: arcade.SpriteList[Entity]
    __sceptre_item: arcade.SpriteList[Entity]

    __monsters: arcade.SpriteList[Monster]

    __grounds: arcade.SpriteList[arcade.Sprite]
    __walls: arcade.SpriteList[arcade.Sprite]
    __holes: arcade.SpriteList[arcade.Sprite]

    __switches: arcade.SpriteList[Switch]
    __gates: arcade.SpriteList[Gate]

    __weapons: list[Weapon]
    __current_weapon: Weapon | None

    __physics_engine: arcade.PhysicsEngineSimple
    __camera: arcade.camera.Camera2D

    __pressed_keys: Final[dict[str, bool]]
    __theme_music: pyglet.media.Player | None

    __show_hitboxes: bool
    __show_navmesh: bool
    __player_is_invicible: bool

    __timer: float

    def __init__(self, map: Map) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.__map = map
        self.__map.initialize_navmesh(3)

        self.__sounds = {
            "collect_crystal":       arcade.load_sound(":resources:sounds/coin5.wav", streaming=False),
            "player_die":            arcade.load_sound(":resources:/sounds/error2.wav", streaming=False),
            "collect_weapon":        arcade.load_sound(":resources:/sounds/upgrade1.wav", streaming=False),
            "blob_absorb_boomerang": arcade.load_sound(":resources:/sounds/phaseJump1.wav", streaming=False),
            "switch_click":          arcade.load_sound("assets/added/switch_click.mp3", streaming=False),
            "mob_die":               arcade.load_sound(":resources:/sounds/hit3.wav", streaming=False),
        }

        arcade.enable_timings()

        self.__world_width  = self.__map.width  * TILE_SIZE
        self.__world_height = self.__map.height * TILE_SIZE

        self.__pressed_keys = {"up": False, "down": False, "right": False, "left": False}
        self.__show_hitboxes = False
        self.__show_navmesh  = False
        self.__player_is_invicible = False

        self.place_sprites()

        self.__physics_engine = arcade.PhysicsEngineSimple(
            player_sprite=self.__player,
            walls=self.__walls
        )
        self.__camera     = arcade.camera.Camera2D()
        self.__gui_camera = arcade.camera.Camera2D()

        self.__theme_music = arcade.play_sound(
            arcade.load_sound("assets/added/game_song.mp3", streaming=True),
            loop=True
        )


    def place_sprites(self) -> None:
        self.__players      = arcade.SpriteList()
        self.__collectables = arcade.SpriteList()
        self.__monsters     = arcade.SpriteList()
        self.__grounds      = arcade.SpriteList(use_spatial_hash=True)
        self.__walls        = arcade.SpriteList(use_spatial_hash=True)
        self.__holes        = arcade.SpriteList(use_spatial_hash=True)
        self.__switches     = arcade.SpriteList(use_spatial_hash=True)
        self.__gates        = arcade.SpriteList(use_spatial_hash=True)

        for cell_j in range(self.__map.height):
            for cell_i in range(self.__map.width):
                cell_x: int = self.__map.i_to_x(cell_i)
                cell_y: int = self.__map.j_to_y(cell_j)
                cell: GridCell = self.__map.get(cell_i, cell_j)

                if cell != GridCell.HOLE:
                    self.__grounds.append(arcade.Sprite(
                        path_or_texture=TEXTURE_GRASS,
                        scale=SCALE,
                        center_x=cell_x, center_y=cell_y
                    ))

                match cell:
                    case GridCell.GRASS:
                        pass

                    case GridCell.BUSH:
                        bush: arcade.Sprite = arcade.Sprite(
                            path_or_texture=TEXTURE_BUSH,
                            scale=SCALE,
                            center_x=cell_x, center_y=cell_y
                        )
                        # custom defined hitbox; feels better and doesnt look worse
                        bush.hit_box = arcade.hitbox.HitBox(((-7.0, -7.0), (7.0, -7.0),
                                                             (7.0, 7.0), (-7.0, 7.0)),
                                                              position=(cell_x, cell_y),
                                                              scale=(SCALE, SCALE))
                        self.__walls.append(bush)

                    case GridCell.HOLE:
                        self.__holes.append(arcade.Sprite(
                            path_or_texture=TEXTURE_HOLE,
                            scale=SCALE,
                            center_x=cell_x, center_y=cell_y
                        ))

                    case GridCell.CRYSTAL:
                        self.__collectables.append(Entity(
                            start_x=cell_x, start_y=cell_y,
                            direction=arcade.Vec2(0, 0), speed=0,
                            animation=CRYSTAL_ANIMATION,
                            id="crystal"
                        ))

                    case GridCell.SWORD:
                        self.__collectables.append(Entity(
                            start_x=cell_x, start_y=cell_y,
                            direction=arcade.Vec2(0, 0), speed=0,
                            animation=SWORD_ITEM_ANIMATION,
                            id="sword"
                        ))

                    case GridCell.BOOMERANG:
                        self.__collectables.append(Entity(
                            start_x=cell_x, start_y=cell_y,
                            direction=arcade.Vec2(0, 0), speed=0,
                            animation=BOOMERANG_ITEM_ANIMATION,
                            id="boomerang"
                        ))

                    case GridCell.SCEPTRE:
                        self.__collectables.append(Entity(
                            start_x=cell_x, start_y=cell_y,
                            direction=arcade.Vec2(0, 0), speed=0,
                            animation=SCEPTRE_ITEM_ANIMATION,
                            id="sceptre"
                        ))

                    case GridCell.VERTICAL_SPINNER:
                        self.__monsters.append(Spinner(
                            start_x=cell_x, start_y=cell_y,
                            direction=arcade.Vec2(0, 1),
                            map=self.__map
                        ))

                    case GridCell.HORIZONTAL_SPINNER:
                        self.__monsters.append(Spinner(
                            start_x=cell_x, start_y=cell_y,
                            direction=arcade.Vec2(1, 0),
                            map=self.__map
                        ))

                    case GridCell.BAT:
                        self.__monsters.append(Bat(start_x=cell_x, start_y=cell_y))

                    case GridCell.BLOB:
                        self.__monsters.append(Blob(start_x=cell_x, start_y=cell_y, map=self.__map))

                    case GridCell.SWITCH:
                        pass
                        # switches are added later

                    case GridCell.GATE:
                        pass
                        # gates are added later

                    case _:
                        assert_never(cell)

        for switch in self.__map.switches:
            center_x: int = switch["x"] * TILE_SIZE + TILE_SIZE // 2
            center_y: int = switch["y"] * TILE_SIZE + TILE_SIZE // 2
            state: bool = switch.get("state", False)
            self.__switches.append(Switch(
                center_x=center_x, center_y=center_y,
                state=state,
                id=switch["id"]
            ))
        for gate in self.__map.gates:
            center_x: int = gate["x"] * TILE_SIZE + TILE_SIZE // 2
            center_y: int = gate["y"] * TILE_SIZE + TILE_SIZE // 2
            self.__gates.append(Gate(
                center_x=center_x, center_y=center_y,
                open_condition=gate["open_if"],
                switches=self.__switches
            ))

        self.__player = Player(
            start_x=self.__map.i_to_x(self.__map.player_start_x),
            start_y=self.__map.i_to_x(self.__map.player_start_y)
        )
        self.__players.append(self.__player)

        self.__sword     = Sword(self.__player)
        self.__boomerang = Boomerang(self.__player)
        self.__sceptre   = Sceptre(self.__player)
        self.__weapons   = []
        self.__weapon_id_mapping = {
            "sword":     self.__sword,
            "boomerang": self.__boomerang,
            "sceptre":   self.__sceptre,
        }
        self.__current_weapon = None

        self.__physics_engine = arcade.PhysicsEngineSimple(
            player_sprite=self.__player,
            walls=self.__walls
        )
        self._remaining_crystals = len([c for c in self.__collectables if c.id == "crystal"])
        self.__monsters.sort(key=lambda m: m.draw_position)
        self.__timer = 0

    def kill_player(self) -> None:
        if self.__player_is_invicible:
            return
        arcade.play_sound(self.__sounds["player_die"])
        time.sleep(0.3)
        self.__player.crystal_count = 0
        self.place_sprites()

    def on_show_view(self) -> None:
        self.window.width  = min(MAX_WINDOW_WIDTH,  self.__world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.__world_height)

    def on_draw(self) -> None:
        self.clear()

        with self.__camera.activate():
            self.__grounds.draw()
            self.__holes.draw()
            self.__walls.draw()
            self.__collectables.draw()
            self.__switches.draw()
            self.__gates.draw()
            self.__monsters.draw()
            if self.__current_weapon is None or not self.__current_weapon.visible or isinstance(self.__current_weapon, Boomerang):
                self.__players.draw()

            if self.__current_weapon is not None and self.__current_weapon.visible:
                arcade.draw_sprite(self.__current_weapon)

            if self.__show_navmesh:
                nodes: list[NavMeshNode] = list(self.__map.navmesh.nodes)
                for node in nodes:
                    pos = arcade.Vec2(
                        self.__map.navmesh.nodes[node]["x"],
                        self.__map.navmesh.nodes[node]["y"]
                    )
                    arcade.draw_circle_filled(pos.x, pos.y, radius=2, color=arcade.color.BLACK)
                    for neighbor in self.__map.navmesh.neighbors(node):
                        arcade.draw_line(
                            pos.x, pos.y,
                            self.__map.navmesh.nodes[neighbor]["x"],
                            self.__map.navmesh.nodes[neighbor]["y"],
                            arcade.color.BLACK, 2
                        )

                for monster in self.__monsters:
                    match monster:
                        case Blob():
                            assert isinstance(monster, Blob)
                            last_target = monster._path_to_target[-1]
                            arcade.draw_rect_filled(
                                arcade.rect.XYWH(last_target.x, last_target.y, 16, 16),
                                (100, 255, 100, 75)
                            )
                            arcade.draw_line_strip(monster._path_to_target, arcade.color.RED, 2)

            if self.__show_hitboxes:
                self.__players.draw_hit_boxes()
                self.__collectables.draw_hit_boxes()
                self.__walls.draw_hit_boxes()
                self.__holes.draw_hit_boxes()
                self.__monsters.draw_hit_boxes()
                if self.__current_weapon is not None:
                    self.__current_weapon.draw_hit_box()

                for monster in self.__monsters:
                    arcade.draw_rect_outline(
                        arcade.rect.LRBT(
                            monster.bottom_left_boundary.x, monster.top_right_boundary.x,
                            monster.top_right_boundary.y,  monster.bottom_left_boundary.y
                        ),
                        arcade.color.WHITE
                    )
                    arcade.draw_line(
                        monster.center_x, monster.center_y,
                        monster.center_x + 50 * monster.direction.x,
                        monster.center_y + 50 * monster.direction.y,
                        arcade.color.BABY_BLUE, 2
                    )
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(monster._target.x, monster._target.y, 16, 16),
                        (255, 100, 100, 75)
                    )

        with self.__gui_camera.activate():
            cursor_index: int = 20

            score_counter = arcade.Text(
                str(self.__player.crystal_count),
                cursor_index, self.window.height - 30,
                arcade.color.WHITE_SMOKE, 25,
                font_name="Kenney Rocket"
            )
            score_counter.draw()
            cursor_index += score_counter.content_width + 40

            for weapon in self.__weapons:
                if weapon == self.__current_weapon:
                    color = arcade.color.WHITE_SMOKE
                else:
                    color = arcade.color.GRAY
                weapon_text = arcade.Text(
                    weapon.display_name,
                    cursor_index, self.window.height - 30,
                    color, 25,
                    font_name="Kenney Mini"
                )
                weapon_text.draw()
                cursor_index += weapon_text.content_width + 20

            arcade.Text(
                f"{self.__timer:.1f}",
                self.window.width - 30, self.window.height - 30,
                arcade.color.WHITE_SMOKE, 25,
                font_name="Kenney Rocket",
                anchor_x="right"
            ).draw()

            if self.__show_hitboxes:
                arcade.Text(
                    str(round(arcade.get_fps())),
                    self.window.width / 2, self.window.height - 30,
                    arcade.color.WHITE_SMOKE, 25
                ).draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.UP | arcade.key.W:
                self.__pressed_keys["up"] = True
            case arcade.key.DOWN | arcade.key.S:
                self.__pressed_keys["down"] = True
            case arcade.key.LEFT | arcade.key.A:
                self.__pressed_keys["right"] = True
            case arcade.key.RIGHT | arcade.key.D:
                self.__pressed_keys["left"] = True

            case arcade.key.R:
                if self.__current_weapon is not None and not self.__current_weapon.active:
                    current_weapon_index = self.__weapons.index(self.__current_weapon)
                    current_weapon_index = (current_weapon_index + 1) % len(self.__weapons)
                    self.__current_weapon = self.__weapons[current_weapon_index]

            case arcade.key.SPACE:
                if self.__current_weapon is not None and not self.__current_weapon.active:
                    self.__current_weapon.use()

            case arcade.key.ESCAPE:
                self.__player_is_invicible = False
                self.kill_player()

            case arcade.key.H:
                self.__show_hitboxes = not self.__show_hitboxes
            case arcade.key.N:
                self.__show_navmesh = not self.__show_navmesh
            case arcade.key.I:
                self.__player_is_invicible = not self.__player_is_invicible

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.UP   | arcade.key.W:
                self.__pressed_keys["up"] = False
            case arcade.key.DOWN | arcade.key.S:
                self.__pressed_keys["down"] = False
            case arcade.key.LEFT | arcade.key.A:
                self.__pressed_keys["right"] = False
            case arcade.key.RIGHT| arcade.key.D:
                self.__pressed_keys["left"] = False

    def on_update(self, delta_time: float) -> None:
        if self._remaining_crystals > 0:
            self.__timer += delta_time

        self.__player.input(self.__pressed_keys)
        self.__player.move()

        if self.__current_weapon is not None:
            self.__current_weapon.move()

        for switch in self.__switches:
            switch.tick()
        for gate in self.__gates:
            gate.tick()
        for collectable in self.__collectables:
            collectable.move()

        for monster in self.__monsters:
            monster.move()
            if isinstance(monster, Blob):
                in_range  = (monster.center - self.__player.center).length() <= 5 * TILE_SIZE
                has_sight = arcade.has_line_of_sight(monster.center, self.__player.center, self.__walls)
                monster.can_see_player = has_sight and in_range
                if monster.can_see_player:
                    monster.last_seen_player = self.__player.center

        # collect collectable
        for collectable in arcade.check_for_collision_with_list(self.__player, self.__collectables):
            collectable.remove_from_sprite_lists()
            if collectable.id in self.__weapon_id_mapping:
                weapon: Weapon = self.__weapon_id_mapping[collectable.id]
                arcade.play_sound(self.__sounds["collect_weapon"])
                assert weapon not in self.__weapons
                self.__weapons.append(weapon)
                self.__current_weapon = weapon
            elif collectable.id == "crystal":
                arcade.play_sound(self.__sounds["collect_crystal"])
                self.__player.crystal_count += 1
                self._remaining_crystals -= 1

        if self.__current_weapon is not None and self.__current_weapon.active:
            for switch in arcade.check_for_collision_with_list(self.__current_weapon, self.__switches):
                last_state = switch.state
                switch.toggle()
                if switch.state != last_state:
                    arcade.play_sound(self.__sounds["switch_click"])
                self.__current_weapon.hit_something = True

            if arcade.check_for_collision_with_list(self.__current_weapon, self.__walls):
                self.__current_weapon.hit_something = True

            match self.__current_weapon:
                case Sceptre():
                    for monster in self.__monsters:
                        if (self.__current_weapon.center - monster.center).length() < 4 * TILE_SIZE:
                            monster.stun(self.__player.center)
                        if isinstance(monster, Blob) and arcade.check_for_collision_with_list(monster, self.__walls):
                            monster.direction = arcade.Vec2(0, 0)
                    self.__current_weapon.hit_something = True

                case Sword():
                    for sprite in arcade.check_for_collision_with_list(self.__current_weapon, self.__monsters):
                        self.__current_weapon.hit_something = True
                        match sprite:
                            case Spinner() | Bat():
                                pass
                            case _:
                                arcade.play_sound(self.__sounds["mob_die"])
                                sprite.remove_from_sprite_lists()

                case Boomerang():
                    for sprite in arcade.check_for_collision_with_list(self.__current_weapon, self.__monsters):
                        assert self.__current_weapon is not None
                        match sprite:
                            case Spinner():
                                self.__current_weapon.hit_something = True

                            case Blob():
                                arcade.play_sound(self.__sounds["blob_absorb_boomerang"])
                                self.__weapons.remove(self.__boomerang)
                                self.__collectables.append(Entity(
                                    start_x=sprite.center_x, start_y=sprite.center_y,
                                    direction=arcade.Vec2(0, 0), speed=0,
                                    animation=BOOMERANG_ITEM_ANIMATION,
                                    id="boomerang"
                                ))
                                self.__boomerang.reset()
                                if len(self.__weapons) > 0:
                                    self.__current_weapon = self.__weapons[0]
                                    self.__current_weapon.hit_something = False
                                else:
                                    self.__current_weapon = None

                            case _:
                                arcade.play_sound(self.__sounds["mob_die"])
                                self.__current_weapon.hit_something = True
                                sprite.remove_from_sprite_lists()

        if arcade.check_for_collision_with_list(self.__player, self.__monsters):
            self.kill_player()

        closest_hole = arcade.get_closest_sprite(self.__player, self.__holes)
        if closest_hole is not None and closest_hole[1] <= 16:
            self.kill_player()

        for gate in self.__gates:
            if not gate.state and gate not in self.__walls:
                self.__walls.append(gate)
            elif gate in self.__walls and gate.state:
                self.__walls.remove(gate)

        self.__physics_engine.update()

        new_camera_x = self.__player.center_x
        new_camera_y = self.__player.center_y

        if self.__world_width <= self.window.width:
            new_camera_x = 480
        else:
            new_camera_x = max(self.window.width / 2, min(new_camera_x, self.__world_width - self.window.width / 2))

        if self.__world_height <= self.window.height:
            new_camera_y = 480
        else:
            new_camera_y = max(self.window.height / 2, min(new_camera_y, self.__world_height - self.window.height / 2))

        self.__camera.position = (new_camera_x, new_camera_y)
