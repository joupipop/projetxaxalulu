from typing import Final
import arcade

arcade.load_font(":resources:fonts/ttf/Kenney/Kenney_Rocket.ttf")
arcade.load_font(":resources:fonts/ttf/Kenney/Kenney_Mini.ttf")



ORIG_TILE_SIZE = (16, 16)

def _load_grid(
    file: str,
    columns: int,
    rows: int,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE
) -> list[arcade.Texture]:
    """
    Loads a texture grid from a spritesheet.

    Args:
        file:
            Path to the spritesheet file name.
        columns:
            The number of columns in the grid.
        rows:
            The number of rows in the grid.
        tile_size (optional):
            The size in pixels of one element of the grid. Defaults to the
            standard tile size of `(16, 16)` that we use in our assets.

    Returns:
        A list of the loaded textures, flattened by row. The texture at grid
        coordinates `(x, y)` is at index `(y * columns) + x` in the list.
    """
    spritesheet = arcade.load_spritesheet(file)
    return spritesheet.get_texture_grid(tile_size, columns, columns * rows)

def _load_animation_strip(
    file: str,
    frame_count: int,
    frame_duration: int = 100,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> arcade.TextureAnimation:
    """
    Loads an animation strip from a line-oriented spritesheet.

    Args:
        file:
            Path to the spritesheet file name.
        frame_count:
            The number of frames in the animation, which should also be the
            number of sub-images in the file.
        frame_duration (optional):
            The duration of each frame in ms (defaults to 100).
        tile_size (optional):
            The size in pixels of one element of the grid, i.e.,  of a frame.
            Defaults to the standard tile size of `(16, 16)` that we use in our
            assets.

    Returns:
        An `arcade.TextureAnimation` representing the full animation.
    """
    grid = _load_grid(file, columns=frame_count, rows=1, tile_size=tile_size)
    keyframes = [arcade.TextureKeyframe(frame, frame_duration) for frame in grid]
    return arcade.TextureAnimation(keyframes)

_overworld_grid = _load_grid("assets/Top_Down_Adventure_Pack_v.1.0/Overworld_Tileset.png", 18, 13)

TEXTURE_GRASS: Final[arcade.Texture] = _overworld_grid[18*1 + 6]
TEXTURE_BUSH: Final[arcade.Texture] = _overworld_grid[18*3 + 5]
TEXTURE_HOLE: Final[arcade.Texture] = _overworld_grid[18*4 + 8]

ANIMATION_PLAYER_IDLE_UP: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_idle_up_anim_strip_6.png", 6)

ANIMATION_PLAYER_IDLE_DOWN: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_idle_down_anim_strip_6.png", 6)
ANIMATION_PLAYER_IDLE_LEFT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_idle_left_anim_strip_6.png", 6)
ANIMATION_PLAYER_IDLE_RIGHT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_idle_right_anim_strip_6.png", 6)

ANIMATION_PLAYER_RUN_UP: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_run_up_anim_strip_6.png", 6)
ANIMATION_PLAYER_RUN_DOWN: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_run_down_anim_strip_6.png", 6)
ANIMATION_PLAYER_RUN_LEFT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_run_left_anim_strip_6.png", 6)
ANIMATION_PLAYER_RUN_RIGHT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_run_right_anim_strip_6.png", 6)

ANIMATION_SWORD_UP: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_attack48_up_anim_strip_6.png", 6, 50, (48, 48))
ANIMATION_SWORD_DOWN: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_attack48_down_anim_strip_6.png", 6, 50, (48, 48))
ANIMATION_SWORD_LEFT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_attack48_left_anim_strip_6.png", 6, 50, (48, 48))
ANIMATION_SWORD_RIGHT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_attack48_right_anim_strip_6.png", 6, 50, (48, 48))
#ANIMATION_SWORD_UP: Final[arcade.TextureAnimation] = \
#    _load_animation_strip("assets/added/char_fire48_up_anim_strip_6.png", 6, 50, (48, 48))
#ANIMATION_SWORD_DOWN: Final[arcade.TextureAnimation] = \
#    _load_animation_strip("assets/added/char_fire48_down_anim_strip_6.png", 6, 50, (48, 48))
#ANIMATION_SWORD_LEFT: Final[arcade.TextureAnimation] = \
#    _load_animation_strip("assets/added/char_fire48_left_anim_strip_6.png", 6, 50, (48, 48))
#ANIMATION_SWORD_RIGHT: Final[arcade.TextureAnimation] = \
#    _load_animation_strip("assets/added/char_fire48_right_anim_strip_6.png", 6, 50, (48, 48))

SWORD_ICON: Final[arcade.Texture] = _load_grid("assets/Top_Down_Adventure_Pack_v.1.0/Overworld_Tileset.png", 18, 13)[1]

CRYSTAL_ANIMATION: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Props_Items_(animated)/crystal_item_anim_strip_6.png", 6)

SWORD_ITEM_ANIMATION: Final[arcade.TextureAnimation] = \
_load_animation_strip("assets/added/sword_item_anim_strip_6_16x32.png", 6, tile_size=(16, 32))

BOOMERANG_ITEM_ANIMATION: Final[arcade.TextureAnimation] = \
_load_animation_strip("assets/added/boomerang_item_anim_strip_6_16x16.png", 6)


SCEPTRE_ITEM_ANIMATION: Final[arcade.TextureAnimation] = \
_load_animation_strip("assets/added/staff_item_anim_strip_6_16x32.png", 6, tile_size=(16, 32))

ANIMATION_SCEPTRE_UP: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/added/char_sceptre48_up_anim_strip_6.png", 6, 50, (48, 48))
ANIMATION_SCEPTRE_DOWN: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/added/char_sceptre48_down_anim_strip_6.png", 6, 50, (48, 48))
ANIMATION_SCEPTRE_RIGHT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/added/char_sceptre48_right_anim_strip_6.png", 6, 50, (48, 48))
ANIMATION_SCEPTRE_LEFT: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/added/char_sceptre48_left_anim_strip_6.png", 6, 50, (48, 48))

SPINNER_ANIMATION: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Enemies_Sprites/Spinner_Sprites/spinner_run_attack_anim_all_dir_strip_8.png", 3)

BOOMERANG_ANIMATION: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/provided/boomerang-sheet.png", 8, 25)

BAT_ANIMATION: Final[arcade.TextureAnimation] = \
    _load_animation_strip("assets/Top_Down_Adventure_Pack_v.1.0/Enemies_Sprites/Pinkbat_Sprites/pinkbat_idle_left_anim_strip_5.png" , 3)

BLOB_ANIMATION:  Final[arcade.TextureAnimation] = \
    _load_animation_strip("/home/lukan/EPFL/BA2/projets/projetxaxalulu/assets/Top_Down_Adventure_Pack_v.1.0/Enemies_Sprites/Pinkslime_Sprites/pinkslime_run_anim_anim_all_dir_strip_6.png" , 6)

TEXTURE_SWITCH_OPEN: Final[arcade.Texture] = _load_grid("assets/added/switch-open.png", 1, 1)[0]
TEXTURE_SWITCH_CLOSED: Final[arcade.Texture] = _load_grid("assets/added/switch-closed.png", 1, 1)[0]

TEXTURE_GATE_OPEN: Final[arcade.Texture] = _load_grid("assets/Top_Down_Adventure_Pack_v.1.0/Tiles_(animated)/Dungeon/iron_gate_closing_anim_strip_8.png", 8, 2)[8]
TEXTURE_GATE_CLOSED: Final[arcade.Texture] = _load_grid("assets/Top_Down_Adventure_Pack_v.1.0/Tiles_(animated)/Dungeon/iron_gate_closing_anim_strip_8.png", 8, 2)[12]
