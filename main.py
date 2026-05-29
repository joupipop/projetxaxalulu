import arcade
import sys
from constants import *
from gameview import GameView
from map import Map, load_map_from_file,InvalidMapFileException

def main() -> None:
    # Create the (unique) Window, setup our GameView, and launch
    window = arcade.Window(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT, WINDOW_TITLE)
    path_to_map_file = sys.argv[1] if len(sys.argv) > 1 else "maps/mainmap.txt"
    try:
        map: Map = load_map_from_file(path_to_map_file)
    except InvalidMapFileException as e:
        print(f"Map file error: {e.message}")
        exit()
    game_view = GameView(map)
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()
