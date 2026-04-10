from constants import TILE_SIZE
import map

def test_coordinate_conversion() -> None:
    world_str: str = """width: 5
height: 5
---
xxxxx
xP  x
x   x
x   x
xxxxx
---""" # 5x5 world
    test_map: map.Map = map.load_map_from_string(world_str)

    assert(test_map.i_to_x(0) == TILE_SIZE//2)
    assert(test_map.i_to_x(2) == 2*TILE_SIZE + TILE_SIZE//2)

    assert(test_map.j_to_y(0) == 4*TILE_SIZE + TILE_SIZE//2)
    assert(test_map.j_to_y(2) == 2*TILE_SIZE + TILE_SIZE//2)


    assert(test_map.x_to_i(TILE_SIZE - 0.01) == 0)
    assert(test_map.x_to_i(TILE_SIZE) == 1)

    assert(test_map.y_to_j(test_map.j_to_y(3)) == 3)
