import copy
import pathlib
from typing import List, Tuple, Self
from enum import Enum


class VisualisationMethod(Enum):
    NoVisualisation = 0,
    EachStep = 1,
    FinalStep = 2


class Location:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def get_neighbours(self) -> Tuple[Self, Self, Self, Self]:
        north = Location(self.row - 1, self.col)
        east = Location(self.row, self.col + 1)
        south = Location(self.row + 1, self.col)
        west = Location(self.row, self.col - 1)
        return north, east, south, west


class GardenMap:
    def __init__(self, map_data: str):
        self.raw_data = map_data
        self.map: List[List[str]] = []
        self.max_row = 0
        self.max_col = 0
        self.start_locations: List[Location] = []
        self.end_locations: List[Location] = []
        self.start_symbol = "S"
        self.start_location: Location = Location(0, 0)
        self.end_symbol = "E"

    def _load_map(self):
        self.map = []
        for line in self.raw_data.split("\n"):
            self.map.append([char for char in line])

        self.max_row = len(self.map)
        self.max_col = len(self.map[0])
        self.start_locations: List[Location] = []
        self.end_locations: List[Location] = []
        self.start_symbol = "S"
        self.start_location: Location = Location(0, 0)
        self.end_symbol = "E"
        for r in range(0, self.max_row):
            for c in range(0, self.max_col):
                if self.map[r][c] == "S":
                    self.start_location = Location(r, c)
                    self.start_locations.append(self.start_location)

    def __is_garden_plot(self, location: Location) -> bool:
        if location.row < 0 or location.row >= self.max_row:
            return False
        if location.col < 0 or location.col >= self.max_col:
            return False

        if self.map[location.row][location.col] == "#":
            return False

        return True

    def __is_available(self, location: Location) -> bool:
        is_plot = self.__is_garden_plot(location)
        if not is_plot:
            return False

        return self.map[location.row][location.col] != self.end_symbol

    def __try_move_to(self, location: Location) -> None:
        if self.__is_available(location):
            self.end_locations.append(location)
            self.map[location.row][location.col] = self.end_symbol

    def __step(self) -> None:
        for sl in self.start_locations:
            n, e, s, w = sl.get_neighbours()
            self.__try_move_to(n)
            self.__try_move_to(e)
            self.__try_move_to(s)
            self.__try_move_to(w)

        start_symbol = self.start_symbol
        end_symbol = self.end_symbol
        self.start_symbol = end_symbol
        self.end_symbol = start_symbol

        self.start_locations = self.end_locations
        self.end_locations = []

    def visualise(self) -> None:
        for r in range(0, self.max_row):
            row = ""
            for char in self.map[r]:
                if char == self.start_symbol:
                    row += "O"
                elif char == self.end_symbol:
                    row += "."
                else:
                    row += char
            print(row)

    def _expand_map(self, exp_factor: int) -> None:
        expanded_map: List[List[str]] = []
        for r in self.map:
            new_row = copy.deepcopy(r)
            for _ in range(2 * exp_factor):
                new_row.extend(copy.deepcopy(r))
            expanded_map.append(new_row)

        for _ in range(2 * exp_factor):
            expanded_map.extend(copy.deepcopy(expanded_map[0:self.max_row]))

        old_start = self.start_location

        new_start_location = Location(old_start.row + exp_factor * self.max_row,
                                      old_start.col + exp_factor * self.max_col)
        for r_idx in range(2 * exp_factor + 1):
            for c_idx in range(2 * exp_factor + 1):
                row = r_idx*self.max_row + old_start.row
                col = c_idx*self.max_col + old_start.col
                if row == new_start_location.row and col == new_start_location.col:
                    continue

                expanded_map[row][col] = "."

        self.start_location = new_start_location
        self.start_locations = []
        self.start_locations.append(new_start_location)
        self.max_row = len(expanded_map)
        self.max_col = len(expanded_map[0])
        self.map = expanded_map

    def explore_steps(self, target: int, visualisation_method: VisualisationMethod, exp_factor: int) -> int:
        self._load_map()
        if exp_factor > 0:
            self._expand_map(exp_factor)

        for step in range(0, target):
            self.__step()
            match visualisation_method:
                case VisualisationMethod.EachStep:
                    self.visualise()
                    print()
                case VisualisationMethod.FinalStep:
                    if step == target - 1:
                        self.visualise()
                        print()

        total_plots = 0
        for r in range(0, self.max_row):
            for char in self.map[r]:
                if char == self.start_symbol:
                    total_plots += 1

        return total_plots

    def _get_reachable_plots_in_area(self, start_row: int, start_col: int) -> int:
        total_plots = 0

        for r in range(start_row, start_row + 131):
            for char in self.map[r][start_col:start_col + 131]:
                if char == self.start_symbol:
                    total_plots += 1

        return total_plots

    def explore_large_steps(self, target: int) -> int:
        self._load_map()
        self._expand_map(2)

        steps_to_extremities = 65 + 2 * 131

        for step in range(0, steps_to_extremities):
            self.__step()

        expansion_factor = (target - 65)//131

        total_plots = 0
        total_plots += self._get_reachable_plots_in_area(0, 2*131)  # N
        total_plots += self._get_reachable_plots_in_area(2*131, 4 * 131)  # E
        total_plots += self._get_reachable_plots_in_area(4 * 131, 2 * 131)  # S
        total_plots += self._get_reachable_plots_in_area(2 * 131, 0)  # W
        total_plots += (expansion_factor**2)*self._get_reachable_plots_in_area(131, 2*131)  # I2
        total_plots += ((expansion_factor - 1) ** 2) * self._get_reachable_plots_in_area(2 * 131, 2 * 131)  # I1
        total_plots += expansion_factor * self._get_reachable_plots_in_area(0, 131)  # NWO
        total_plots += expansion_factor * self._get_reachable_plots_in_area(0, 3 * 131)  # NEO
        total_plots += expansion_factor * self._get_reachable_plots_in_area(3 * 131, 0)  # SWO
        total_plots += expansion_factor * self._get_reachable_plots_in_area(3 * 131, 4 * 131)  # SEO
        total_plots += (expansion_factor - 1) * self._get_reachable_plots_in_area(131, 131)  # NWI
        total_plots += (expansion_factor - 1) * self._get_reachable_plots_in_area(131, 3 * 131)  # NEI
        total_plots += (expansion_factor - 1) * self._get_reachable_plots_in_area(3 * 131, 131)  # SWI
        total_plots += (expansion_factor - 1) * self._get_reachable_plots_in_area(3 * 131, 3 * 131)  # SEI

        return total_plots


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
gm = GardenMap(puzzle_input)

step_goal = 6
if file_name == "input":
    step_goal = 64

print(f"Part 1: {gm.explore_steps(step_goal, VisualisationMethod.NoVisualisation, 0)}")

if file_name == "input":
    step_goal = 26501365
    print(f"Part 2: {gm.explore_large_steps(step_goal)}")
else:
    print(f"Part 2 algorithm does not work on input_small")
