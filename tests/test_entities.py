from map import *
from arcade import SpriteList
from constants import TILE_SIZE
from entities import *

def test_input_up_and_left() -> None:
    player: Player = Player(0, 0)
    player.input({"up": True, "down": False, "right": True, "left": False})
    assert player.direction == arcade.Vec2(1, 1)

    player.input({"up": False, "down": True, "right": False, "left": True})
    assert player.direction == arcade.Vec2(-1, -1)
    player.input({"up": False, "down": False, "right": False, "left": False})
    assert player.direction == arcade.Vec2(0, 0)

def test_reached_target() -> None:
    monster: Monster = Monster(50, 50, arcade.Vec2(0, 0), arcade.Vec2(0, 0), 0, BAT_ANIMATION, 0)
    monster._target = arcade.Vec2(51, 51)
    assert(monster.reached_target())

    monster._target = arcade.Vec2(100, 100)
    assert(not monster.reached_target())

def test_blob_pathfind() -> None:
    map: Map = load_map_from_string("""
width: 9
height: 9
---
xxxxxxxxx
x       x
x       x
x  xxx  x
x  xBx  x
x  xxx  x
x       x
xP      x
xxxxxxxxx
---
                                    """)
    map.initialize_navmesh(3)
    blob: Blob = Blob(map.i_to_x(4), map.j_to_y(4), map)
    assert(blob._target == arcade.Vec2(map.i_to_x(4), map.j_to_y(4)))

def test_gate_evaluate() -> None:
    switches = SpriteList()
    switches.append(Switch(0, 0, True, "first"))
    switches.append(Switch(0, 0, False, "second"))
    condition: Condition = {
    "open_if": [
        {
            "and": [
                {
                    "or": [
                        {"not": [{"switch_is_on": "first"}]},
                        {"switch_is_on": "second"},
                    ]
                },
                {"switch_is_on": "first"},
            ]
        }
    ]
} # type: ignore (mypy cant check recursion this deep)
    test_gate: Gate = Gate(0, 0, condition, switches)
    assert(test_gate.evaluate(condition) == False)
