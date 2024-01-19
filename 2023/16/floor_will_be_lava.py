import pathlib
import sys
from enum import Enum
from typing import List, Set, Dict, Optional


class Direction(Enum):
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4


tile_entry_exits: Dict[Direction, Dict[str, List[Direction]]] = {
    Direction.NORTH: {
        ".": [Direction.NORTH],
        "/": [Direction.EAST],
        "\\": [Direction.WEST],
        "|": [Direction.NORTH],
        "-": [Direction.WEST, Direction.EAST]
    },
    Direction.EAST: {
        ".": [Direction.EAST],
        "/": [Direction.NORTH],
        "\\": [Direction.SOUTH],
        "|": [Direction.NORTH, Direction.SOUTH],
        "-": [Direction.EAST]
    },
    Direction.SOUTH: {
        ".": [Direction.SOUTH],
        "/": [Direction.WEST],
        "\\": [Direction.EAST],
        "|": [Direction.SOUTH],
        "-": [Direction.WEST, Direction.EAST]
    },
    Direction.WEST: {
        ".": [Direction.WEST],
        "/": [Direction.SOUTH],
        "\\": [Direction.NORTH],
        "|": [Direction.NORTH, Direction.SOUTH],
        "-": [Direction.WEST]
    }
}


class Tile:
    def __init__(self, char: str, r: int, c: int):
        self.row = r
        self.col = c
        self.tile = char
        self.entry_directions: Set[Direction] = set()
        self.is_energised = False

    def enter_from(self, entry_direction: Direction) -> List[Direction]:
        # If we've already entered from this direction then there's nothing left to process
        if entry_direction in self.entry_directions:
            return []

        self.is_energised = True
        self.entry_directions.add(entry_direction)
        return tile_entry_exits[entry_direction][self.tile]

    def reset(self):
        self.entry_directions = set()
        self.is_energised = False


class TileEntry:
    def __init__(self, tile: Tile, direction: Direction):
        self.tile = tile
        self.entry_direction = direction


class Grid:
    def __init__(self, all_rows: str):
        self.tiles: List[List[Tile]] = []

        for r_idx, line in enumerate(all_rows.split()):
            row = []
            for c_idx, c in enumerate(line):
                row.append(Tile(c, r_idx, c_idx))
            self.tiles.append(row)

        self.max_row = len(self.tiles)
        self.max_col = len(self.tiles[0])

    def get_tile_in_direction(self, start_tile: Tile, direction: Direction) -> Optional[Tile]:
        match direction:
            case Direction.NORTH:
                if start_tile.row > 0:
                    return self.tiles[start_tile.row - 1][start_tile.col]
            case Direction.EAST:
                if start_tile.col < self.max_col - 1:
                    return self.tiles[start_tile.row][start_tile.col + 1]
            case Direction.SOUTH:
                if start_tile.row < self.max_row - 1:
                    return self.tiles[start_tile.row + 1][start_tile.col]
            case Direction.WEST:
                if start_tile.col > 0:
                    return self.tiles[start_tile.row][start_tile.col - 1]

        return None

    def enter_from(self, entry_directions: List[TileEntry]):
        next_entry_directions: List[TileEntry] = []
        for tile_entry in entry_directions:
            exit_directions = tile_entry.tile.enter_from(tile_entry.entry_direction)
            for exit_direction in exit_directions:
                exit_tile = self.get_tile_in_direction(tile_entry.tile, exit_direction)
                if exit_tile:
                    next_entry_directions.append(TileEntry(exit_tile, exit_direction))

        if len(next_entry_directions) > 0:
            self.enter_from(next_entry_directions)

    def get_energised_tile_count(self) -> int:
        total = 0
        for r in self.tiles:
            for t in r:
                if t.is_energised:
                    total += 1

        return total

    def reset(self) -> None:
        for r in self.tiles:
            for c in r:
                c.reset()

    def maximise_energised_cells(self) -> int:
        # The default recursion limit in Python is 1000, however some of the configurations
        # in the input result in more than 1000 recursive calls
        sys.setrecursionlimit(2000)
        current_max = 0
        start_tile = self.tiles[0][0]
        heading = Direction.EAST
        entry_direction = Direction.SOUTH

        while True:
            self.reset()

            self.enter_from([TileEntry(start_tile, entry_direction)])
            energised_count = self.get_energised_tile_count()
            if energised_count > current_max:
                current_max = energised_count

            if start_tile.row == 0 and start_tile.col == 0 and heading == Direction.NORTH:
                break

            next_tile = self.get_tile_in_direction(start_tile, heading)
            if next_tile:
                start_tile = next_tile
            else:
                match heading:
                    case Direction.EAST:
                        heading = Direction.SOUTH
                        entry_direction = Direction.WEST
                    case Direction.SOUTH:
                        heading = Direction.WEST
                        entry_direction = Direction.NORTH
                    case Direction.WEST:
                        heading = Direction.NORTH
                        entry_direction = Direction.EAST

        return current_max


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
grid = Grid(puzzle_input)

start_direction = [TileEntry(grid.tiles[0][0], Direction.EAST)]
grid.enter_from(start_direction)

print(f"Part 1: {grid.get_energised_tile_count()}")

print(f"Part 2: {grid.maximise_energised_cells()}")
