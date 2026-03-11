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


class Player(Entity):
    def __init__(self, start_x: int, start_y: int) -> None:
        super().__init__(start_x, start_y, 0, 0, 4, ANIMATION_PLAYER_IDLE_DOWN)
