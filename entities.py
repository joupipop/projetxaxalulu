from typing import Final
import arcade
import math
import random

from constants import *
from textures import *
from map import Map, GridCell

class Entity(arcade.TextureAnimationSprite):
    speed: float # in pixels per frame
    direction: arcade.Vec2
    random_tick_range: tuple[int, int]
    tick_counter: int
    tick_limit: int
    @property
    def center(self) -> arcade.Vec2:
        return arcade.Vec2(self.center_x, self.center_y)
    @center.setter
    def center(self, other: arcade.Vec2) -> None:
        self.center_x = other.x
        self.center_y = other.y

    def __init__(self, start_x: int | float, start_y: int | float, direction: arcade.Vec2, speed: int | float, sprite_texture: arcade.TextureAnimation) -> None:
        super().__init__(start_x, start_y, SCALE, sprite_texture)
        self.direction = direction
        self.speed = speed

        self.random_tick_range = (1200, 1800) # 20 to 30 secs
        self.tick_counter = 0
        self.tick_limit = random.randint(self.random_tick_range[0], self.random_tick_range[1])

    def move(self) -> None:
        self.change_x = self.direction.x * self.speed
        self.change_y = self.direction.y * self.speed
        self.center = self.center + arcade.Vec2(self.change_x, self.change_y)
        self.update_animation()

        self.tick_counter += 1
        if self.tick_counter > self.tick_limit:
            self.tick_counter = 0
            self.tick_limit = random.randint(self.random_tick_range[0], self.random_tick_range[1])
    def random_tick(self) -> bool:
        return self.tick_counter == self.tick_limit

class Player(Entity):
    facing_direction: arcade.Vec2
    previous_direction: arcade.Vec2
    crystal_count: int
    def __init__(self, start_x: int, start_y: int) -> None:
        super().__init__(start_x, start_y, arcade.Vec2(0, -1), PLAYER_MOVEMENT_SPEED, ANIMATION_PLAYER_IDLE_DOWN)
        self.facing_direction = arcade.Vec2(0, -1)
        self.previous_direction = arcade.Vec2(0, -1)
        self.crystal_count = 0

    def input(self, pressed_keys: list[bool]) -> None:
        self.direction = arcade.Vec2(pressed_keys[3] - pressed_keys[2], pressed_keys[0] - pressed_keys[1])

    def move(self) -> None:
        animation_set: list[arcade.TextureAnimation]
        super().move()

        if self.direction != arcade.Vec2(0, 0):
            if self.direction.x == 0 or self.direction.y == 0:
                self.facing_direction = arcade.Vec2(self.direction.x, self.direction.y)
            else:
                self.facing_direction = arcade.Vec2(self.direction.x, 0)
        if self.previous_direction == self.direction:
            return
        self.previous_direction = arcade.Vec2(self.direction.x, self.direction.y)
        if self.direction == arcade.Vec2(0, 0):
            animation_set = [ANIMATION_PLAYER_IDLE_UP, ANIMATION_PLAYER_IDLE_DOWN, ANIMATION_PLAYER_IDLE_LEFT, ANIMATION_PLAYER_IDLE_RIGHT]
        else:
            animation_set = [ANIMATION_PLAYER_RUN_UP, ANIMATION_PLAYER_RUN_DOWN, ANIMATION_PLAYER_RUN_LEFT, ANIMATION_PLAYER_RUN_RIGHT]
        if self.facing_direction == arcade.Vec2(0, 1):
            self.animation = animation_set[0]
        if self.facing_direction == arcade.Vec2(0, -1):
            self.animation = animation_set[1]
        if self.facing_direction == arcade.Vec2(-1, 0):
            self.animation = animation_set[2]
        if self.facing_direction == arcade.Vec2(1, 0):
            self.animation = animation_set[3]

class Spinner(Entity):
    start_boundary_x: int
    start_boundary_y: int
    end_boundary_x: int
    end_boundary_y: int # works for both horizontal and vertical spinners


    def __init__(self, start_x: int, start_y: int, direction: arcade.Vec2, map: Map) -> None:
        super().__init__(start_x, start_y, direction, 3, SPINNER_ANIMATION)
        self.initialise(map)

    def initialise(self, map: Map) -> None:
        search_index: int = 0
        next_cell_coords: list = [0, 0]
        next_cell: GridCell | None = GridCell.GRASS
        while next_cell != GridCell.BUSH:
            search_index += 1
            next_cell_coords = [map.x_to_i(self.center_x) + self.direction.x * search_index, map.y_to_j(self.center_y) - self.direction.y * search_index]
            next_cell = map.get(next_cell_coords[0], next_cell_coords[1])

        self.end_boundary_x = map.i_to_x(next_cell_coords[0] - self.direction.x)
        self.end_boundary_y = map.j_to_y(next_cell_coords[1] + self.direction.y) # positive y direction means negative j direction

        search_index: int = 0
        next_cell_coords: list = [0, 0]
        next_cell: GridCell | None = GridCell.GRASS
        while next_cell != GridCell.BUSH:
            search_index -= 1
            next_cell_coords = [map.x_to_i(self.center_x) + self.direction.x * search_index, map.y_to_j(self.center_y) - self.direction.y * search_index]
            next_cell = map.get(next_cell_coords[0], next_cell_coords[1])

        self.start_boundary_x = map.i_to_x(next_cell_coords[0] + self.direction.x)
        self.start_boundary_y = map.j_to_y(next_cell_coords[1] - self.direction.y)


    def move(self) -> None:
        spinner_in_bounds: bool = (self.start_boundary_x <= self.center_x <= self.end_boundary_x
                               and self.start_boundary_y <= self.center_y <= self.end_boundary_y)
        if spinner_in_bounds:
            super().move()
        else:
            self.direction = arcade.Vec2(-self.direction.x, -self.direction.y)
            super().move()

class Bat(Entity):
    start_boundary_x: int
    start_boundary_y: int
    end_boundary_x: int
    end_boundary_y: int
    target: arcade.Vec2

    def __init__(self, start_x: int, start_y: int) -> None:
        super().__init__(start_x, start_y, arcade.Vec2(0, -1), 1, BAT_ANIMATION)
        self.start_boundary_x = start_x - BAT_RANGE * TILE_SIZE - TILE_SIZE//2
        self.end_boundary_x = start_x + BAT_RANGE * TILE_SIZE - TILE_SIZE//2

        self.start_boundary_y = start_y - BAT_RANGE * TILE_SIZE - TILE_SIZE//2
        self.end_boundary_y = start_y + BAT_RANGE * TILE_SIZE - TILE_SIZE//2

        self.target = arcade.Vec2(random.randint(self.start_boundary_x, self.end_boundary_x),
                               random.randint(self.start_boundary_y, self.end_boundary_y))
        self.direction = (self.target - self.center).normalize()

    def move(self) -> None:
        if (self.center - self.target).length() <= 16 or self.random_tick():
            self.target = arcade.Vec2(random.randint(self.start_boundary_x, self.end_boundary_x),
                                   random.randint(self.start_boundary_y, self.end_boundary_y))

        self.direction = (self.target - self.center).normalize()
        super().move()

class Blob(Entity):
    start_boundary_x: int
    start_boundary_y: int
    end_boundary_x: int
    end_boundary_y: int
    map: Map
    target: arcade.Vec2
    path_to_target: list[arcade.Vec2]
    path_index: int
    can_see_player: bool
    last_seen_player: arcade.Vec2

    def __init__(self, start_x: int, start_y: int, map: Map) -> None:
        super().__init__(start_x, start_y, arcade.Vec2(0, -1), 0.5, BLOB_ANIMATION)
        self.start_boundary_x = start_x - BLOB_RANGE * TILE_SIZE - TILE_SIZE//2
        self.end_boundary_x = start_x + BLOB_RANGE * TILE_SIZE + TILE_SIZE//2

        self.start_boundary_y = start_y - BLOB_RANGE * TILE_SIZE - TILE_SIZE//2
        self.end_boundary_y = start_y + BLOB_RANGE * TILE_SIZE + TILE_SIZE//2

        self.map = map

        self.target = arcade.Vec2(random.randint(self.start_boundary_x, self.end_boundary_x),
                               random.randint(self.start_boundary_y, self.end_boundary_y))

        self.target = arcade.Vec2(542, 293)
        self.path_to_target = self.map.calculate_path(self.center, self.target)

        self.path_index = 0

        self.can_see_player = False


    def move(self) -> None:
        if self.can_see_player:
            self.target = self.last_seen_player
        elif (self.center - self.target).length() <= 16 or self.random_tick():
            self.target = arcade.Vec2(random.randint(self.start_boundary_x, self.end_boundary_x),
                                   random.randint(self.start_boundary_y, self.end_boundary_y))
            target_cell: GridCell | None = self.map.get(self.map.x_to_i(self.target.x), self.map.y_to_j(self.target.y))
            print(target_cell)
            if target_cell != GridCell.GRASS:
                self.target = arcade.Vec2(random.randint(self.start_boundary_x, self.end_boundary_x),
                       random.randint(self.start_boundary_y, self.end_boundary_y))
            potential_path_to_target = self.map.calculate_path(self.center, self.target)
            if potential_path_to_target != []: # a path was found
                self.path_to_target = potential_path_to_target
            self.path_index = 0

        self.new_path_ending = self.map.calculate_path(self.path_to_target[self.path_index], self.target)

        if self.path_index == 0 or self.path_index == len(self.path_to_target)-1:
            #self.path_to_target = self.new_path_ending
            pass
        else:
            self.path_to_target = self.path_to_target[:self.path_index] + self.new_path_ending

        temp_target = self.path_to_target[self.path_index]
        if (self.center - temp_target).length() <= 5:
            self.path_index += 1
        self.direction = (temp_target - self.center).normalize()
        super().move()
        self.can_see_player = False

class Weapon(Entity):
    owner: Player
    state: int
    hit_something: bool
    display_name: str

    def __init__(self, owner: Player, speed: int, animation: arcade.TextureAnimation) -> None:
        super().__init__(owner.center_x, owner.center_y, owner.facing_direction, speed, animation)
        self.owner = owner
        self.state = 0
        self.hit_something = False

class Boomerang(Weapon):
    distance: int
    def __init__(self, owner: Player) -> None:
        super().__init__(owner, 6, BOOMERANG_ANIMATION)
        self.distance = 0
        self.display_name = "boomerang"

    def move(self) -> None:
        if self.state == 0: # inactive
            self.center = self.owner.center
            self.direction = self.owner.facing_direction
            self.hit_something = False
        elif self.state == 1: # launching
            if self.hit_something:
                self.hit_something = False
                self.state = 2
                self.move()
                return

            super().move()
            self.distance += self.speed
            if self.distance >= 7*TILE_SIZE:
                self.state = 2
                self.distance = 0

        elif self.state == 2: # returning
            distance_from_player = (self.owner.center - self.center).length()
            if distance_from_player <= 16:
                self.state = 0
                self.distance = 0
                return
            self.direction = (self.owner.center - self.center).normalize()
            super().move()

class Sword(Weapon):
    owner: Player
    state: int
    previous_direction: arcade.Vec2
    def __init__(self, owner: Player) -> None:
        super().__init__(owner, 0, ANIMATION_SWORD_UP)
        self.display_name = "sword"
    def sync_hit_box_to_texture(self) -> None:
        # reimplement sync hit box to texture to choose appropriate keyframe
        self.texture = self.animation._keyframes[3].texture
        self.hit_box = arcade.hitbox.RotatableHitBox(
            self.texture.hit_box_points,
            position=self._position,
            angle=self.angle,
            scale=self._scale,
        )
    def move(self) -> None:
        if self.state == 0:
            self.previous_direction = self.direction
            self.direction = self.owner.facing_direction
            self.center = self.owner.center + 10 * self.direction
            if self.previous_direction != self.direction:
                # change texture direction
                if self.direction == arcade.Vec2(0, 1):
                    self.animation = ANIMATION_SWORD_UP
                if self.direction == arcade.Vec2(0, -1):
                    self.animation = ANIMATION_SWORD_DOWN
                if self.direction == arcade.Vec2(-1, 0):
                    self.animation = ANIMATION_SWORD_LEFT
                if self.direction == arcade.Vec2(1, 0):
                    self.animation = ANIMATION_SWORD_RIGHT

        elif self.state == 1:
            self.update_animation()
            # block player movements
            self.owner.center = self.center - 10 * self.direction
            if self.time >= 300/1000: #30 ms
                self.state = 0
                self.time =  0

class Switch(arcade.Sprite):
    state: bool
    can_be_used: bool
    cooldown_timer: int  # otherwise if it gets hit on the boomerangs return i like flips out
    id: str

    def __init__(self, center_x: int | float, center_y: int | float, state: bool, id: str) -> None:
        super().__init__(TEXTURE_SWITCH_OPEN, SCALE, center_x, center_y)
        self.state = state
        self.can_be_used = True
        self.cooldown_timer = 0
        self.id = id

    def tick(self) -> None:
        if not self.can_be_used:
            self.cooldown_timer += 1
        if self.cooldown_timer >= 20:
            self.can_be_used = True
            self.cooldown_timer = 0

    def toggle(self) -> None:
        if not self.can_be_used:
            return
        self.state = not self.state
        if self.state == 1:
            self.texture = TEXTURE_SWITCH_CLOSED
        else:
            self.texture = TEXTURE_SWITCH_OPEN
        self.can_be_used = False

class Gate(arcade.Sprite):
    state: bool
    open_condition: dict
    switches: arcade.SpriteList[Switch]

    def __init__(self, center_x: int | float, center_y: int | float, open_condition: dict, switches: arcade.SpriteList[Switch]) -> None:
        super().__init__(TEXTURE_GATE_CLOSED, SCALE, center_x, center_y)
        self.open_condition = open_condition
        self.switches = switches
        print(self.open_condition)

    def evaluate(self, condition: dict) -> bool:
        if "and" in condition:
            return (self.evaluate(condition["and"][0])
                and self.evaluate(condition["and"][1]))
        elif "or" in condition:
            return (self.evaluate(condition["or"][0])
                 or self.evaluate(condition["or"][1]))
        elif "not" in condition:
            return not self.evaluate(condition["not"][0])
        elif "switch_is_on" in condition:
            for switch in self.switches:
                if switch.id == condition["switch_is_on"]:
                    return switch.state
        return False
    def tick(self) -> None:
        self.state = self.evaluate(self.open_condition)
        if self.state:
            self.texture = TEXTURE_GATE_OPEN
        else:
            self.texture = TEXTURE_GATE_CLOSED
