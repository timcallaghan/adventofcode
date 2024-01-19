import pathlib
from typing import List, Self, Optional
import operator


class Coords:
    def __init__(self, r: int, c: int):
        self.row = r
        self.col = c

    def subtract(self, other: Self):
        self.row -= other.row
        self.col -= other.col


class Edge:
    def __init__(self, r: int, c: int, hex_colour: str, is_vertical: bool):
        self.coords = Coords(r, c)
        self.colour = hex_colour
        self.is_vertical = is_vertical

    def subtract(self, other: Coords):
        self.coords.subtract(other)


class DigPlan:
    def __init__(self, plan_data: str):
        self.plan_data = plan_data
        self.perimeter: List[Edge] = []
        self.grid: List[List[str]] = []
        self.max_coords: Optional[Coords] = None

    @staticmethod
    def translate_hex_to_uldr(line: str) -> str:
        line = line.replace("(#", "").replace(")", "")
        _, _, hex_dir = line.strip().split(" ")
        hex_val = int(hex_dir[0:-1], 16)
        dir_int = int(hex_dir[-1])
        direction = "R"
        match dir_int:
            case 1:
                direction = "D"
            case 2:
                direction = "L"
            case 3:
                direction = "U"

        return f"{direction} {hex_val} (#123450)"

    def _build_perimeter(self, use_hex: bool) -> None:
        print("Building perimeter...")
        self.perimeter = []
        self.grid = []
        self.max_coords = None

        lines = self.plan_data.split("\n")

        previous_vertical_direction = ""
        for r_idx in range(len(lines) - 1, -1, -1):
            ln = self.translate_hex_to_uldr(lines[r_idx]) if use_hex else lines[r_idx]

            if ln.startswith("U"):
                previous_vertical_direction = "U"
                break
            if ln.startswith("D"):
                previous_vertical_direction = "D"
                break

        # We trace around the perimeter and also determine if a vertical edge is preset.
        #  - If the direction is U or D then this is true.
        #  - If the direction is L or R then we need to consider the direction of the U/D points that
        #    connect to this horizontal segment of the perimeter:
        #    - (D, U) - False
        #    - (U, D) - False
        #    - (U, U) - True
        #    - (D, D) - True
        previously_horizontal = False
        previously_vertical = False
        current_row = 0
        current_col = 0
        for line in lines:
            line = self.translate_hex_to_uldr(line) if use_hex else line
            direction, amount, colour = line.split(" ")
            is_vertical = direction == "U" or direction == "D"
            if is_vertical:
                if previously_horizontal and previous_vertical_direction == direction:
                    self.perimeter[-1].is_vertical = True
                previously_horizontal = False
                previous_vertical_direction = direction
                previously_vertical = True
            else:
                if not previously_horizontal and previously_vertical:
                    self.perimeter[-1].is_vertical = False

                previously_vertical = False
                previously_horizontal = True

            for step in range(int(amount)):
                match direction:
                    case "R":
                        current_col += 1
                    case "D":
                        current_row += 1
                    case "L":
                        current_col -= 1
                    case "U":
                        current_row -= 1

                self.perimeter.append(Edge(current_row, current_col, colour, is_vertical))

        if self.perimeter[-1].coords.row == self.perimeter[0].coords.row:
            self.perimeter[-1].is_vertical = False

        # Translate to plan starting at origin
        min_coords = self.get_min_coords()
        for e in self.perimeter:
            e.subtract(min_coords)

        self.perimeter.sort(key=operator.attrgetter('coords.row', 'coords.col'))
        self.max_coords = self.get_max_coords()

        current_col = 0
        current_row = 0
        self.grid.append([])
        for e in self.perimeter:
            if e.coords.row != current_row:
                for _ in range(current_col, self.max_coords.col + 1):
                    self.grid[-1].append(".")

                self.grid.append([])
                for _ in range(0, e.coords.col):
                    self.grid[-1].append(".")

                self.grid[-1].append("|" if e.is_vertical else "#")
                current_col = e.coords.col + 1
                current_row = e.coords.row
            else:
                for _ in range(current_col, e.coords.col):
                    self.grid[-1].append(".")

                self.grid[-1].append("|" if e.is_vertical else "#")
                current_col = e.coords.col + 1

        for _ in range(current_col, self.max_coords.col + 1):
            self.grid[-1].append(".")

        print("Perimeter built!")

    def visualise(self):
        for r in self.grid:
            print("".join(r))

    def get_min_coords(self) -> Coords:
        min_row = 0
        min_col = 0
        for e in self.perimeter:
            if e.coords.row < min_row:
                min_row = e.coords.row

            if e.coords.col < min_col:
                min_col = e.coords.col

        return Coords(min_row, min_col)

    def get_max_coords(self) -> Coords:
        max_row = 0
        max_col = 0
        for e in self.perimeter:
            if e.coords.row > max_row:
                max_row = e.coords.row

            if e.coords.col > max_col:
                max_col = e.coords.col

        return Coords(max_row, max_col)

    def is_inside_perimeter(self, r: int, c: int) -> bool:
        grid_char = self.grid[r][c]
        if grid_char == "#" or grid_char == "|":
            return True

        edge_crossings = 0
        for c_idx in range(c + 1, len(self.grid[0])):
            if self.grid[r][c_idx] == "|":
                edge_crossings += 1

        return edge_crossings % 2 == 1

    def get_dug_out_volume(self, use_hex: bool) -> int:
        self._build_perimeter(use_hex)

        volume = 0
        for r_idx in range(len(self.grid)):
            for c_idx in range(len(self.grid[0])):
                if self.is_inside_perimeter(r_idx, c_idx):
                    volume += 1
                    if volume % 1000000 == 0:
                        print(f"Current volume: {volume}")

        return volume


file_name = "../input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
dig_plan = DigPlan(puzzle_input)
print(f"Part 1: {dig_plan.get_dug_out_volume(False)}")
print(f"Part 2: {dig_plan.get_dug_out_volume(True)}")
