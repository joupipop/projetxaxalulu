from dataclasses import dataclass
from typing import Final
import arcade
import math
import random

from constants import *
from textures import *
from map import Map, GridCell

class Entity(arcade.TextureAnimationSprite):
    direction: arcade.Vec2
    __speed: Final[int | float] # in pixels per frame
    id: str | None
    @property
    def center(self) -> arcade.Vec2:
        return arcade.Vec2(self.center_x, self.center_y)
    @center.setter
    def center(self, other: arcade.Vec2) -> None:
        self.center_x = other.x
        self.center_y = other.y

    def __init__(self, start_x: int | float, start_y: int | float, direction: arcade.Vec2, speed: int | float, animation: arcade.TextureAnimation, id: str | None = None) -> None:
        super().__init__(start_x, start_y, SCALE, animation)
        self.direction = direction
        self.__speed = speed
        self.id = id

    def move(self) -> None:
        self.change_x = self.direction.x * self.__speed
        self.change_y = self.direction.y * self.__speed
        self.center = self.center + arcade.Vec2(self.change_x, self.change_y)
        self.update_animation()

class Player(Entity):
    crystal_count: int
    facing_direction: arcade.Vec2
    __previous_direction: arcade.Vec2
    def __init__(self, start_x: int, start_y: int) -> None:
        super().__init__(start_x, start_y, arcade.Vec2(0, -1), PLAYER_MOVEMENT_SPEED, ANIMATION_PLAYER_IDLE_DOWN)
        self.crystal_count = 0
        self.facing_direction = arcade.Vec2(0, -1)
        self.__previous_direction = arcade.Vec2(0, -1)

    def input(self, pressed_keys: dict[str, bool]) -> None:
        self.direction = arcade.Vec2(pressed_keys["left"] - pressed_keys["right"], pressed_keys["up"] - pressed_keys["down"])

    def move(self) -> None:
        animation_set: list[arcade.TextureAnimation]
        # dont use super().move() because physic engine does it already
        self.change_x = self.direction.x * PLAYER_MOVEMENT_SPEED
        self.change_y = self.direction.y * PLAYER_MOVEMENT_SPEED

        self.update_animation()

        if self.direction != arcade.Vec2(0, 0):
            if self.direction.x == 0 or self.direction.y == 0:
                self.facing_direction = arcade.Vec2(self.direction.x, self.direction.y)
            else:
                self.facing_direction = arcade.Vec2(self.direction.x, 0)
        if self.__previous_direction == self.direction:
            return
        self.__previous_direction = arcade.Vec2(self.direction.x, self.direction.y)
        if self.direction == arcade.Vec2(0, 0):
            animation_set = [ANIMATION_PLAYER_IDLE_UP, ANIMATION_PLAYER_IDLE_DOWN, ANIMATION_PLAYER_IDLE_LEFT, ANIMATION_PLAYER_IDLE_RIGHT]
        else:
            animation_set = [ANIMATION_PLAYER_RUN_UP, ANIMATION_PLAYER_RUN_DOWN, ANIMATION_PLAYER_RUN_LEFT, ANIMATION_PLAYER_RUN_RIGHT]
        match self.facing_direction:
            case arcade.Vec2(0, 1):
                self.animation = animation_set[0]
            case arcade.Vec2(0, -1):
                self.animation = animation_set[1]
            case arcade.Vec2(-1, 0):
                self.animation = animation_set[2]
            case arcade.Vec2(1, 0):
                self.animation = animation_set[3]

class Monster(Entity):
    bottom_left_boundary: Final[arcade.Vec2]
    top_right_boundary: Final[arcade.Vec2]
    _target: arcade.Vec2
    _is_stunned: bool
    _stun_timer: int
    draw_position: Final[int]

    def __init__(self, start_x: int, start_y: int, bottom_left_boundary: arcade.Vec2, top_right_boundary: arcade.Vec2, speed: int | float, animation: arcade.TextureAnimation, draw_position: int = 0) -> None:
        super().__init__(start_x, start_y, arcade.Vec2(0, -1), speed, animation)
        self.bottom_left_boundary = bottom_left_boundary
        self.top_right_boundary = top_right_boundary
        self._target = bottom_left_boundary
        self._is_stunned = False
        self._stun_timer = 0
        self.draw_position = draw_position

    def reached_target(self, distance: int | float = 5) -> bool:
        return (self.center-self._target).length() <= distance

    def move(self) -> None:
        if self._is_stunned:
            self.stunned_move()
            return
        self.direction = (self._target - self.center).normalize()
        super().move()


    def stun(self, origin: arcade.Vec2) -> None:
        self.direction = (self.center - origin).normalize()
        self._is_stunned = True

    def stunned_move(self) -> None:
        if self._stun_timer < 8: # knockback portion
            self.change_x = self.direction.x * STUN_KNOCKBACK_SPEED
            self.change_y = self.direction.y * STUN_KNOCKBACK_SPEED
            self.center = self.center + arcade.Vec2(self.change_x, self.change_y)

        if self._stun_timer >= 150:
            self._is_stunned = False
            self._stun_timer = 0

        self._stun_timer += 1
        self.time = 0

class Bat(Monster):
    def __init__(self, start_x: int, start_y: int) -> None:
        bottom_left_boundary = arcade.Vec2(start_x - BAT_RANGE * TILE_SIZE + TILE_SIZE//2,
                                           start_y - BAT_RANGE * TILE_SIZE + TILE_SIZE//2)
        top_right_boundary = arcade.Vec2(start_x + BAT_RANGE * TILE_SIZE - TILE_SIZE//2,
                                         start_y + BAT_RANGE * TILE_SIZE - TILE_SIZE//2)

        super().__init__(start_x, start_y, bottom_left_boundary, top_right_boundary, BAT_SPEED, BAT_ANIMATION, 2)

        self._target = arcade.Vec2(random.randint(int(self.bottom_left_boundary.x), int(self.top_right_boundary.x)),
                                      random.randint(int(self.bottom_left_boundary.y), int(self.top_right_boundary.y)))

    def move(self) -> None:
        if self.reached_target():
            self._target = arcade.Vec2(random.randint(int(self.bottom_left_boundary.x), int(self.top_right_boundary.x)),
                                      random.randint(int(self.bottom_left_boundary.y), int(self.top_right_boundary.y)))
        super().move()

class Spinner(Monster):
    def __init__(self, start_x: int, start_y: int, direction: arcade.Vec2, map: Map) -> None:
        search_index: int = 0
        next_cell_coords: list = [0, 0]
        next_cell: GridCell | None = GridCell.GRASS
        while next_cell != GridCell.BUSH and next_cell != None:
            search_index += 1
            next_cell_coords = [map.x_to_i(start_x) + direction.x * search_index, map.y_to_j(start_y) - direction.y * search_index]
            next_cell = map.get(next_cell_coords[0], next_cell_coords[1])

        top_right_boundary: arcade.Vec2 = arcade.Vec2(map.i_to_x(next_cell_coords[0] - direction.x),
                                                      map.j_to_y(next_cell_coords[1] + direction.y)) # positive y direction means negative j direction
        search_index: int = 0
        next_cell_coords: list = [0, 0]
        next_cell: GridCell | None = GridCell.GRASS
        while next_cell != GridCell.BUSH:
            search_index -= 1
            next_cell_coords = [map.x_to_i(start_x) + direction.x * search_index, map.y_to_j(start_y) - direction.y * search_index]
            next_cell = map.get(next_cell_coords[0], next_cell_coords[1])

        bottom_left_boundary: arcade.Vec2 = arcade.Vec2(map.i_to_x(next_cell_coords[0] + direction.x),
                                                        map.j_to_y(next_cell_coords[1] - direction.y))

        super().__init__(start_x, start_y, bottom_left_boundary, top_right_boundary, SPINNER_SPEED, SPINNER_ANIMATION, 1)
        self._target = top_right_boundary

    def move(self) -> None:
        if self.reached_target():
            if self._target == self.bottom_left_boundary:
                self._target = self.top_right_boundary
            else:
                self._target = self.bottom_left_boundary
        super().move()

    def stunned_move(self) -> None:
        if self._stun_timer >= 160:
            self._is_stunned = False
            self._stun_timer = 0

        self._stun_timer += 1
        self.time = 0


class Blob(Monster):
    _path_to_target: list[arcade.Vec2] # accessed externally by debug screen
    __path_index: int
    can_see_player: bool
    last_seen_player: arcade.Vec2
    __map: Final[Map]
    __attainable_cells: Final[set[arcade.Vec2]]

    def __init__(self, start_x: int, start_y: int, map: Map) -> None:
        bottom_left_boundary = arcade.Vec2(start_x - BLOB_RANGE * TILE_SIZE + TILE_SIZE//2 + 1,
                                           start_y - BLOB_RANGE * TILE_SIZE + TILE_SIZE//2 + 1)
        top_right_boundary = arcade.Vec2(start_x + BLOB_RANGE * TILE_SIZE - TILE_SIZE//2 - 1,
                                         start_y + BLOB_RANGE * TILE_SIZE - TILE_SIZE//2 - 1)
        # +/- 1's are to make sure x_to_i and y_to_j snap to the correct cell
        super().__init__(start_x, start_y, bottom_left_boundary, top_right_boundary, 0.5, BLOB_ANIMATION, 0)
        self.__map = map
        attainable_cells: set[arcade.Vec2] = set()
        # calculate all possible targets in boundary
        for j in range(self.__map.y_to_j(top_right_boundary.y), self.__map.y_to_j(bottom_left_boundary.y)):
            for i in range(self.__map.x_to_i(bottom_left_boundary.x), self.__map.x_to_i(top_right_boundary.x)):
                cell: arcade.Vec2 = arcade.Vec2(self.__map.i_to_x(i), self.__map.j_to_y(j))
                path_to_cell: list[arcade.Vec2] = self.__map.calculate_path(self.center, cell)
                if path_to_cell != []:
                    attainable_cells.add(cell)
        self.__attainable_cells = attainable_cells

        self.__map = map
        self._target = random.choice(tuple(self.__attainable_cells))
        self._path_to_target = [self.center]
        self.__path_index = 0
        self.can_see_player = False

    def move(self) -> None:
        if self.__path_index == len(self._path_to_target) - 1: # reached end
            final_target: arcade.Vec2 = random.choice(tuple(self.__attainable_cells))
            self._path_to_target = self.__map.calculate_path(self.center, final_target)
            self.__path_index = 0

        if self.can_see_player:
            potential_path_to_target = self.__map.calculate_path(self.center, self.last_seen_player)

            if potential_path_to_target != [] and potential_path_to_target[0] != self._path_to_target[0]: # a new path was found
                self._path_to_target = potential_path_to_target
                self.__path_index = 0

        if self.reached_target(0.4):
            self.center = self._target
            self.__path_index += 1

        self._target = self._path_to_target[self.__path_index]

        super().move()


class Weapon(Entity):
    owner: Final[Player]
    _state: int
    hit_something: bool
    display_name: Final[str]

    def __init__(self, owner: Player, speed: int, animation: arcade.TextureAnimation, display_name: str) -> None:
        super().__init__(owner.center_x, owner.center_y, owner.facing_direction, speed, animation)
        self.owner = owner
        self._state = 0
        self.hit_something = False
        self.display_name = display_name
    @property
    def active(self) -> bool: # determines from the state if the weapon can kill
        return self._state != 0
    @property
    def visible(self) -> bool:
        return self._state != 0

    def use(self) -> None:
        self._state = 1

class Boomerang(Weapon):
    __distance: int

    def __init__(self, owner: Player) -> None:
        super().__init__(owner, BOOMERANG_SPEED, BOOMERANG_ANIMATION, "boomerang")
        self.__distance = 0

    def move(self) -> None:
        if self._state == 0: # inactive
            self.center = self.owner.center
            self.direction = self.owner.facing_direction
            self.hit_something = False
        elif self._state == 1: # launching
            if self.hit_something:
                self.hit_something = False
                self._state = 2
                self.move()
                return

            super().move()
            self.__distance += BOOMERANG_SPEED
            if self.__distance >= 7*TILE_SIZE:
                self._state = 2
                self.__distance = 0

        elif self._state == 2: # returning
            distance_from_player = (self.owner.center - self.center).length()
            if distance_from_player <= 16:
                self._state = 0
                self.__distance = 0
                return
            self.direction = (self.owner.center - self.center).normalize()
            super().move()
    def reset(self) -> None:
        self._state = 0
        self.__distance = 0

class Sword(Weapon):
    __previous_direction: arcade.Vec2
    def __init__(self, owner: Player) -> None:
        super().__init__(owner, 0, ANIMATION_SWORD_UP, "sword")
    def sync_hit_box_to_texture(self) -> None:
        # reimplement sync hit box to texture to choose appropriate keyframe
        self.texture = self.animation._keyframes[3].texture
        self.hit_box = arcade.hitbox.RotatableHitBox(
            self.texture.hit_box_points,
            position=self._position,
            angle=self.angle,
            scale=self._scale,
        )
        self.texture = self.animation._keyframes[0].texture

    def move(self) -> None:
        if self._state == 0: # inactive
            self.__previous_direction = self.direction
            self.direction = self.owner.facing_direction
            self.center = self.owner.center + 10 * self.direction
            if self.__previous_direction != self.direction:
                # change texture direction
                match self.direction:
                    case arcade.Vec2(0, 1):
                        self.animation = ANIMATION_SWORD_UP
                    case arcade.Vec2(0, -1):
                        self.animation = ANIMATION_SWORD_DOWN
                    case arcade.Vec2(-1, 0):
                        self.animation = ANIMATION_SWORD_LEFT
                    case arcade.Vec2(1, 0):
                        self.animation = ANIMATION_SWORD_RIGHT

        elif self._state == 1: # active
            self.update_animation()
            # block player movements
            self.owner.center = self.center - 10 * self.direction
            if self.time >= 300/1000: #300 ms
                self._state = 0
                self.time =  0


class Sceptre(Weapon):
    _previous_direction: arcade.Vec2
    def __init__(self, owner: Player) -> None:
        super().__init__(owner, 0, ANIMATION_SWORD_UP, "sceptre")

    def move(self) -> None:
        if self._state == 0:
            self.__previous_direction = self.direction
            self.direction = self.owner.facing_direction
            self.center = self.owner.center
            if self.__previous_direction != self.direction:
                # change texture direction
                match self.direction:
                    case arcade.Vec2(0, 1):
                        self.animation = ANIMATION_SCEPTRE_UP
                    case arcade.Vec2(0, -1):
                        self.animation = ANIMATION_SCEPTRE_DOWN
                    case arcade.Vec2(-1, 0):
                        self.animation = ANIMATION_SCEPTRE_LEFT
                    case arcade.Vec2(1, 0):
                        self.animation = ANIMATION_SCEPTRE_RIGHT
        else:
            self.update_animation()
            # block player movements

            self.owner.center = self.center
            if self.time >= 150/1000: # 150 ms
                self._state = 2
            if self.time >= 300/1000: #300 ms
                self._state = 0
                self.time =  0


        if self._state == 2: # use staff (for only one frame)
            if self.hit_something:
                self._state = 1
                self.hit_something = False

    def use(self) -> None:
        if self.owner.crystal_count < 1:
            self._state = 0
        else:
            self.owner.crystal_count -= 1
            self._state = 1

    @property
    def active(self) -> bool:
        return self._state == 2

class Switch(arcade.Sprite):
    state: bool
    __can_be_used: bool
    __cooldown_timer: int  # otherwise if it gets hit on the boomerangs return i like flips out
    id: Final[str]

    def __init__(self, center_x: int | float, center_y: int | float, state: bool, id: str) -> None:
        self.state = state
        self.__can_be_used = True
        self.__cooldown_timer = 0
        self.id = id
        super().__init__(TEXTURE_SWITCH_CLOSED if self.state else TEXTURE_SWITCH_OPEN, SCALE, center_x, center_y)


    def tick(self) -> None:
        if not self.__can_be_used:
            self.__cooldown_timer += 1
        if self.__cooldown_timer >= 20:
            self.__can_be_used = True
            self.__cooldown_timer = 0

    def toggle(self) -> None:
        if not self.__can_be_used:
            return
        self.state = not self.state
        if self.state:
            self.texture = TEXTURE_SWITCH_CLOSED
        else:
            self.texture = TEXTURE_SWITCH_OPEN
        self.__can_be_used = False



type Condition = dict[str, list[Condition] | dict[str, str]]

class Gate(arcade.Sprite):
    state: bool
    __open_condition: Final[Condition]
    __switches: Final[arcade.SpriteList[Switch]]

    def __init__(self, center_x: int | float, center_y: int | float, open_condition: Condition, switches: arcade.SpriteList[Switch]) -> None:
        super().__init__(TEXTURE_GATE_CLOSED, SCALE, center_x, center_y)
        self.__open_condition = open_condition
        self.__switches = switches
        self.state = False

    def evaluate(self, condition: Condition) -> bool:
        if "and" in condition:
            assert(isinstance(condition["and"], list))
            return (self.evaluate(condition["and"][0])
                and self.evaluate(condition["and"][1]))
        elif "or" in condition:
            assert(isinstance(condition["or"], list))
            return (self.evaluate(condition["or"][0])
                 or self.evaluate(condition["or"][1]))
        elif "not" in condition:
            assert(isinstance(condition["not"], list))
            return not self.evaluate(condition["not"][0])
        elif "switch_is_on" in condition:
            for switch in self.__switches:
                if switch.id == condition["switch_is_on"]:
                    return switch.state
        return False

    def tick(self) -> None:
        self.state = self.evaluate(self.__open_condition)
        if self.state:
            self.texture = TEXTURE_GATE_OPEN
        else:
            self.texture = TEXTURE_GATE_CLOSED
