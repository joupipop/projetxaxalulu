import yaml
import arcade
import math
from dataclasses import dataclass

import networkx as nx
from enum import Enum
from constants import *


def pixels_to_grid(x: int | float) -> int:
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
    HOLE = 6
    BAT = 7
    BLOB = 8
    SWITCH = 9
    GATE = 10
@dataclass(frozen=True)
class NavMeshNode2:
    x: float
    y: float


@dataclass(frozen=True)
class NavMeshNode:
    i: int
    j: int # coordinates of cell in which the node is

    k: int
    l: int # intra-cell coordinates of the node


class Map:
    width: int
    height: int
    cells: tuple[tuple[GridCell]]

    player_start_x: int
    player_start_y: int

    navmesh: nx.Graph[NavMeshNode]
    resolution: int # should be odd

    switches: list[dict]
    gates: list[dict]

    def __init__(self, width: int, height: int, cells: tuple[tuple[GridCell]], player_start_x: int, player_start_y: int, switches: list[dict], gates: list[dict]) -> None:
        self.width = width
        self.height = height
        self.cells = cells
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y
        self.navmesh = nx.Graph()
        self.switches = switches
        self.gates = gates

    def i_to_x(self, i: int) -> int:
        return i * TILE_SIZE + (TILE_SIZE // 2)

    def j_to_y(self, j: int) -> int:
        return (self.height - j - 1) * TILE_SIZE + (TILE_SIZE // 2)

    def x_to_i(self, x: int | float) -> int:
        return int(x) // TILE_SIZE

    def y_to_j(self, y: int | float) -> int:
        return self.height - int(y) // TILE_SIZE - 1

    def get(self, i:int, j:int) -> GridCell | None:
        if 0 <= i < self.width and 0 <= j < self.height:
            return self.cells[j][i]
        return None

    def initialize_navmesh(self, resolution: int) -> None:
        obstacles: list[GridCell] = [GridCell.BUSH, GridCell.HOLE, GridCell.GATE]
        self.resolution = resolution
        for j in range(len(self.cells)):
            for i in range(len(self.cells[j])):
                cell: GridCell = self.cells[j][i]
                if cell in obstacles:
                    continue
                for l in range(resolution):
                    for k in range(resolution):
                        node: NavMeshNode = NavMeshNode(i, j, k, l)

                        node_x: float = i*TILE_SIZE + (2*k + 1)*TILE_SIZE/(2*resolution)
                        node_y: float = (self.height-j)*TILE_SIZE - (2*(l+1)+1)*TILE_SIZE/(2*resolution) + TILE_SIZE/resolution # formule absurde je ne la comprend pas mais faut pas trop y toucher

                        # check that not to close to bush
                        to_close_to_bush: bool = False
                        for m in [-1, 0, +1]:
                            for n in [-1, 0, +1]:
                                if i+n < 0 or j+n >= self.width or j+m < 0 or j+m >= self.height:
                                    continue
                                if self.cells[j+m][i+n] in obstacles:
                                    distance_node_to_bush: float = arcade.Vec2(node_x-self.i_to_x(i+n), node_y-self.j_to_y(j+m)).length()
                                    if distance_node_to_bush < TILE_SIZE:
                                        to_close_to_bush = True
                        if to_close_to_bush:
                            continue
                        self.navmesh.add_node(node, x=node_x, y=node_y)

                        # connect all neighbours
                        for m in [-1, 0, +1]:
                            for n in [-1, 0, +1]: # iterate over all possible neighbours
                                if m == 0 == n:
                                    continue
                                neighbour_i = i
                                neighbour_j = j
                                neighbour_k = k + n
                                neighbour_l = l + m
                                # treat edge cases
                                if neighbour_k < 0:
                                    neighbour_k = resolution - 1
                                    neighbour_i = i - 1
                                if neighbour_k >= resolution:
                                    neighbour_k = 0
                                    neighbour_i = i + 1
                                if neighbour_l < 0:
                                    neighbour_l = resolution - 1
                                    neighbour_j = j - 1
                                if neighbour_l >= resolution:
                                    neighbour_l = 0
                                    neighbour_j = j + 1

                                if neighbour_i < 0 or neighbour_i >= self.width:
                                    continue
                                if neighbour_j < 0 or neighbour_j >= self.height:
                                    continue
                                # if neighbour is a part of the graph, we can connect to it
                                neighbour: NavMeshNode = NavMeshNode(neighbour_i, neighbour_j,
                                                                     neighbour_k, neighbour_l)
                                if neighbour in self.navmesh.nodes:
                                    neighbour_x: float = self.navmesh.nodes[neighbour]["x"]
                                    neighbour_y: float = self.navmesh.nodes[neighbour]["y"]

                                    distance: float = arcade.Vec2(node_x - neighbour_x, node_y - neighbour_y).length()
                                    self.navmesh.add_edge(node, neighbour, weight=distance)
    def calculate_path(self, start: arcade.Vec2, end: arcade.Vec2) -> list[arcade.Vec2]:

        path: list[arcade.Vec2] = []
        # calculate starting navmesh node (in same cell as start but closest to end)
        start_cell_center_node: NavMeshNode = NavMeshNode(self.x_to_i(start.x), self.y_to_j(start.y), self.resolution//2, self.resolution//2)
        if start_cell_center_node not in self.navmesh.nodes:
            print("no path", start)
            return path
        best_node = start_cell_center_node

        for node in nx.neighbors(self.navmesh, start_cell_center_node):
            if end.distance((self.navmesh.nodes[node]["x"], self.navmesh.nodes[node]["y"])) < end.distance((self.navmesh.nodes[best_node]["x"], self.navmesh.nodes[best_node]["y"])):
                best_node = node
        start_node = start_cell_center_node
        # calculate end navmesh node (center of end cell is enough)

        end_node: NavMeshNode = NavMeshNode(self.x_to_i(end.x), self.y_to_j(end.y), self.resolution//2, self.resolution//2)
        #print(self.navmesh.nodes[end_node]["x"], self.navmesh.nodes[end_node]["y"])

        if start_node not in self.navmesh.nodes or end_node not in self.navmesh.nodes:
            return path
        node_path: list[NavMeshNode] = nx.dijkstra_path(self.navmesh, start_node, end_node)
        for node in node_path:
            path.append(arcade.Vec2(self.navmesh.nodes[node]["x"], self.navmesh.nodes[node]["y"]))
        path.append(end)
        return path

def load_map_from_string(map_text: str) -> Map:
    width: int
    height: int
    cells: list[list[GridCell]] = [[]] # will later be turned into a tuple array

    player_start_x: int
    player_start_y: int

    switches: list[dict] = [{}]
    gates: list[dict] = [{}]

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

        data = yaml.load(configuration, Loader=yaml.SafeLoader)
        for key in data:
            value = data[key]
            match key:
                case "width":
                    width = int(value)
                case "height":
                    height = int(value)
                case "switches":
                    switches = data[key]
                case "gates":
                    gates = data[key]
                case _:
                    raise InvalidMapFileException(f"Unknown configuration option \"{key}\".")
        i_index = 0
        j_index = 0
        # coordinate system centered in top left corner
        for cell in world:
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
                case 'O':
                    cells[j_index].append(GridCell.HOLE)
                case 'v':
                    cells[j_index].append(GridCell.BAT)
                case 'B':
                    cells[j_index].append(GridCell.BLOB)
                case '^':
                    cells[j_index].append(GridCell.SWITCH)
                case '|':
                    cells[j_index].append(GridCell.GATE)

                case '\n':
                    cells.append([])
                    j_index += 1
                    # check if width is consistent with configuration
                    if i_index != width:
                        raise InvalidMapFileException(f"Incorrect map width. {i_index} != {width}")

                    i_index = 0
                    continue
                case _:
                    raise InvalidMapFileException(f"Unknown cell \"{cell}\".")
            i_index += 1

        final_map = Map(width, height, tuple(map(tuple, cells)), player_start_x, player_start_y, switches, gates)
        return final_map
    except InvalidMapFileException as e:
        print(f"Map file error: {e.message}")
        exit()


def load_map_from_file(file_path: str) -> Map:
    with open(file_path, 'r') as file:
        return load_map_from_string(file.read())
