from textwrap import dedent
from map import load_map_from_string, Map
import arcade

from gameview import GameView

def test_collect_crystals(window: arcade.Window) -> None:
    map: Map = load_map_from_string(dedent("""\
        width: 4
        height: 3
        ---
        xxxx
        xP*x
        xxxx
        ---
    """))
    view = GameView(map)
    window.show_view(view)

    INITIAL_CRYSTAL_COUNT = 1

    # Make sure we have the amount of coins we expect at the start
    assert view._remaining_crystals == INITIAL_CRYSTAL_COUNT

    # Start moving right
    view.on_key_press(arcade.key.RIGHT, 0)

    # Let the game run for 1 second
    window.test(60)

    # We should have collected the first coin
    assert view._remaining_crystals == INITIAL_CRYSTAL_COUNT - 1
