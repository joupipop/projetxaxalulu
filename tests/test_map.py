import pytest
from textwrap import dedent
from pytiled_parser import Grid
from tests.test_entities import GridCell, InvalidMapFileException
import map
from constants import TILE_SIZE

def test_coordinate_conversion() -> None:
    world_str: str = """\
        width: 5
        height: 5
        ---
        xxxxx
        xP  x
        x   x
        x   x
        xxxxx
        ---
                    """ # 5x5 world
    test_map: map.Map = map.load_map_from_string(dedent(world_str))

    assert(test_map.i_to_x(0) == TILE_SIZE//2)
    assert(test_map.i_to_x(2) == 2*TILE_SIZE + TILE_SIZE//2)

    assert(test_map.j_to_y(0) == 4*TILE_SIZE + TILE_SIZE//2)
    assert(test_map.j_to_y(2) == 2*TILE_SIZE + TILE_SIZE//2)


    assert(test_map.x_to_i(TILE_SIZE - 0.01) == 0)
    assert(test_map.x_to_i(TILE_SIZE) == 1)

    assert(test_map.y_to_j(test_map.j_to_y(3)) == 3)

def test_map_parser() -> None:
    world_str: str = """\
        width: 13
        height: 1
        switches:
          - id: james
            x: 8
            y: 0
        gates:
          - id: thilbert
            x: 9
            y: 0
            open_if:
              - switch_is_on: james
        ---
        x*sSPOvB^|TV/
        ---
                     """

    test_map: map.Map = map.load_map_from_string(dedent(world_str))
    print(test_map.cells)
    assert(test_map.cells == ((GridCell.BUSH, GridCell.CRYSTAL, GridCell.HORIZONTAL_SPINNER, GridCell.VERTICAL_SPINNER,
                              GridCell.GRASS, GridCell.HOLE, GridCell.BAT, GridCell.BLOB, GridCell.SWITCH,
                              GridCell.GATE, GridCell.SWORD, GridCell.BOOMERANG, GridCell.SCEPTRE),))

def test_map_errors() -> None:
    too_wide_world: str = """\
        width: 2
        height: 1
        ---
        Pxx
        ---
        """
    with pytest.raises(InvalidMapFileException):
        test_map: map.Map = map.load_map_from_string(dedent(too_wide_world))

    too_short_world: str = """\
        width: 3
        height: 2
        ---
        Pxx
        ---
        """
    with pytest.raises(InvalidMapFileException):
        test_map: map.Map = map.load_map_from_string(dedent(too_short_world))

    no_player_world: str = """\
        width: 3
        height: 1
        ---
        xxx
        ---
        """
    with pytest.raises(InvalidMapFileException):
        test_map: map.Map = map.load_map_from_string(dedent(no_player_world))

    no_switch_world: str = """\
        width: 3
        height: 1
        switches:
          - id: idontexist
            x: 0
            y: 0
        ---
        xxx
        ---
        """
    with pytest.raises(InvalidMapFileException):
        test_map: map.Map = map.load_map_from_string(dedent(no_switch_world))
