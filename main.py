import arcade
import sys
from constants import *
from gameview import GameView

def main() -> None:
    # Create the (unique) Window, setup our GameView, and launch
    window = arcade.Window(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT, WINDOW_TITLE)
    path_to_map_file = sys.argv[1] if len(sys.argv) > 1 else "maps/mainmap.txt"
    game_view = GameView(path_to_map_file)
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()
