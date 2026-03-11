from typing import Final
import arcade

from constants import *
from textures import *


class Entity(arcade.TextureAnimationSprite):
    speed: int # in pixels per frame

    def __init__(self, start_x: int, start_y: int, change_x: int, change_y: int, speed: int, sprite_texture: arcade.TextureAnimation) -> None:
        super().__init__(start_x, start_y, SCALE, sprite_texture)
        self.change_x = change_x
        self.change_y = change_y
        self.speed = speed

    def move(self) -> None:
        self.center_x += self.change_x
        self.center_y += self.change_y

        self.update_animation()


class Player(Entity):
    def __init__(self, start_x: int, start_y: int) -> None:
        super().__init__(start_x, start_y, 0, 0, 4, ANIMATION_PLAYER_IDLE_DOWN)

    def input(self, pressed_keys: list[bool]) -> None:
        direction_x: int = pressed_keys[3] - pressed_keys[2]
        direction_y: int = pressed_keys[0] - pressed_keys[1]
        self.change_x = direction_x * self.speed
        self.change_y = direction_y * self.speed

        if direction_x == 0 or direction_y == 0:
            return
        # normalize change_x,y
        self.change_x *= INVSQRT2
        self.change_y *= INVSQRT2
