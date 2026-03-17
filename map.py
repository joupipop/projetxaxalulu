from enum import Enum
from constants import *

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

def pixels_to_grid(x: int) -> int:
    return int((x - (TILE_SIZE // 2)) / TILE_SIZE)

class InvalidMapFileException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class GridCell(Enum):
    GRASS = 1
    BUSH = 2
    CRYSTAL = 3
    HORIZONTAL_SPINNER = 4
    VERTICAL_SPINNER = 5

class Map:
    width: int
    height: int
    cells: tuple[tuple[GridCell]]

    player_start_x: int
    player_start_y: int

    def __init__(self, width: int, height: int, cells: tuple[tuple[GridCell]], player_start_x: int, player_start_y: int) -> None:
        self.width = width
        self.height = height
        self.cells = cells
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y

    def get(self, x:int, y:int) -> GridCell | None:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None

def load_map_from_string(map_text: str) -> Map:
    width: int
    height: int
    cells: list[list[GridCell]] = [[]] # will later be turned into a tuple array

    player_start_x: int
    player_start_y: int
    try:
        configuration_end_index = map_text.find("---") - 1

        # check if find method returned -1 (substring not found)
        if configuration_end_index < 0:
            raise InvalidMapFileException("Delimiter \"---\" not found.")

        configuration = map_text[0:configuration_end_index]

        world_start_index = configuration_end_index + 5
        world_end_index = map_text.find("---", world_start_index)

        # check if find method returned -1 (substring not found)
        if world_end_index < 0:
            raise InvalidMapFileException("Delimiter \"---\" not found.")

        world = map_text[world_start_index:world_end_index]


        for line in configuration.split('\n'):
            delimiter_index = line.find(': ')
            if delimiter_index < 0:
                raise InvalidMapFileException(f"Invalid configuration format \"{line}\".")

            config_key = line[0:delimiter_index]
            config_value = line[delimiter_index+2:]
            match config_key:
                case "width":
                    width = int(config_value)
                case "height":
                    height = int(config_value)
                case _:
                    raise InvalidMapFileException(f"Unknown configuration option \"{config_key}\".")
        i_index = 0
        j_index = 0
        for cell in world:
            # coordinate system centered in top left corner
            match cell:
                case ' ':
                    cells[j_index].append(GridCell.GRASS)
                case 'x':
                    cells[j_index].append(GridCell.BUSH)
                case '*':
                    cells[j_index].append(GridCell.CRYSTAL)
                case 's':
                    cells[j_index].append(GridCell.HORIZONTAL_SPINNER)
                case 'S':
                    cells[j_index].append(GridCell.VERTICAL_SPINNER)
                case 'P':
                    cells[j_index].append(GridCell.GRASS)
                    player_start_x = i_index
                    player_start_y = height - j_index
                case '\n':
                    cells.append([])
                    j_index += 1
                    # check if width is consistent with configuration
                    if i_index != width:
                        raise InvalidMapFileException(f"Incorrect map width. {i_index}")

                    i_index = -1
                case _:
                    raise InvalidMapFileException(f"Unknown cell \"{cell}\".")
            i_index += 1

        final_map = Map(width, height, tuple(map(tuple, cells)), player_start_x, player_start_y)
        return final_map
    except InvalidMapFileException as e:
        print(f"Map file error: {e.message}")
        exit()


def load_map_from_file(file_path: str) -> Map:
    with open(file_path, 'r') as file:
        return load_map_from_string(file.read())
