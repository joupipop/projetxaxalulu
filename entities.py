from typing import Final
import arcade
import math

from constants import *
from textures import *
from map import Map, GridCell, pixels_to_grid, grid_to_pixels

class Vector2D:
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    def normalise(self) -> Vector2D: # returns a normalised copy or zero if is zero
        norm: float = math.sqrt(self.x**2 + self.y**2)
        if norm != 0:
            return Vector2D(self.x/norm, self.y/norm)
        return Vector2D(0, 0)

class Entity(arcade.TextureAnimationSprite):
    speed: int # in pixels per frame

    def __init__(self, start_x: int, start_y: int, direction: Vector2D, speed: int, sprite_texture: arcade.TextureAnimation) -> None:
        super().__init__(start_x, start_y, SCALE, sprite_texture)
        self.direction = direction
        self.speed = speed

    def move(self) -> None:
        self.change_x = self.direction.normalise().x * self.speed
        self.change_y = self.direction.normalise().y * self.speed
        self.center_x += self.change_x
        self.center_y += self.change_y

        self.update_animation()


class Player(Entity):
    def __init__(self, start_x: int, start_y: int) -> None:
        super().__init__(start_x, start_y, Vector2D(0, -1), 4, ANIMATION_PLAYER_IDLE_DOWN)

    def input(self, pressed_keys: list[bool]) -> None:
        self.direction.x = float(pressed_keys[3] - pressed_keys[2])
        self.direction.y = float(pressed_keys[0] - pressed_keys[1])


class Spinner(Entity):
    start_boundary_x: int
    start_boundary_y: int
    end_boundary_x: int
    end_boundary_y: int # works for both horizontal and vertical spinners


    def __init__(self, start_x: int, start_y: int, direction: Vector2D, map: Map) -> None:
        super().__init__(start_x, start_y, direction, 3, SPINNER_ANIMATION)
        self.initialise(map)

    def initialise(self, map: Map) -> None:
        search_index: int = 0
        next_cell_coords: list = [0, 0]
        next_cell: GridCell | None = GridCell.GRASS
        while next_cell != GridCell.BUSH:
            search_index += 1
            next_cell_coords = [int(pixels_to_grid(int(self.center_x)) + self.direction.x * search_index), int(pixels_to_grid(int(self.center_y)) + self.direction.y * search_index)]
            next_cell = map.get(next_cell_coords[0], next_cell_coords[1])

        self.end_boundary_x = grid_to_pixels(next_cell_coords[0] - self.direction.x)
        self.end_boundary_y = grid_to_pixels(next_cell_coords[1] - self.direction.y)

        search_index: int = 0
        next_cell_coords: list = [0 ,0]
        next_cell: GridCell | None = GridCell.GRASS
        while next_cell != GridCell.BUSH:
            search_index -= 1
            next_cell_coords = [int(pixels_to_grid(int(self.center_x)) + self.direction.x * search_index), int(pixels_to_grid(int(self.center_y)) + self.direction.y * search_index)]
            next_cell = map.get(next_cell_coords[0], next_cell_coords[1])

        self.start_boundary_x = grid_to_pixels(next_cell_coords[0] + self.direction.x)
        self.start_boundary_y = grid_to_pixels(next_cell_coords[1] + self.direction.y)


    def move(self) -> None:
        spinner_in_bounds: bool = (self.start_boundary_x <= self.center_x <= self.end_boundary_x
                               and self.start_boundary_y <= self.center_y <= self.end_boundary_y)
        if spinner_in_bounds:
            super().move()
        else:
            self.direction = Vector2D(-self.direction.x, -self.direction.y)
            self.center_x += self.direction.x * self.speed
            self.center_y += self.direction.y * self.speed
