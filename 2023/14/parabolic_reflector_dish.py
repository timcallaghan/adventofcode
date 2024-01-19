import copy
import pathlib
from typing import Tuple, Dict, List


def get_rock_data_as_string(rocks: List[List[str]]) -> str:
    rows = []
    for cell_data in rocks:
        row_data = "".join(cell_data)
        rows.append(row_data)

    return "\n".join(rows)


def tilt_north(rocks: List[List[str]]) -> None:
    # Stores next row index for each column
    next_slots = [0] * len(rocks[0])
    for r_idx in range(len(rocks)):
        row = rocks[r_idx]
        for c_idx in range(len(row)):
            cell_value = row[c_idx]
            if cell_value == "O":
                if next_slots[c_idx] != r_idx:
                    rocks[next_slots[c_idx]][c_idx] = "O"
                    rocks[r_idx][c_idx] = "."

                next_slots[c_idx] += 1
            elif cell_value == "#":
                next_slots[c_idx] = r_idx + 1


def tilt_west(rocks: List[List[str]]) -> None:
    # Stores next column index for each row
    next_slots = [0] * len(rocks)
    for c_idx in range(len(rocks[0])):
        for r_idx in range(len(rocks)):
            cell_value = rocks[r_idx][c_idx]
            if cell_value == "O":
                if next_slots[r_idx] != c_idx:
                    rocks[r_idx][next_slots[r_idx]] = "O"
                    rocks[r_idx][c_idx] = "."

                next_slots[r_idx] += 1
            elif cell_value == "#":
                next_slots[r_idx] = c_idx + 1


def tilt_south(rocks: List[List[str]]) -> None:
    # Stores next row index for each column
    next_slots = [len(rocks) - 1] * len(rocks[0])
    for r_idx in range(len(rocks)-1, -1, -1):
        row = rocks[r_idx]
        for c_idx in range(len(row)):
            cell_value = row[c_idx]
            if cell_value == "O":
                if next_slots[c_idx] != r_idx:
                    rocks[next_slots[c_idx]][c_idx] = "O"
                    rocks[r_idx][c_idx] = "."

                next_slots[c_idx] -= 1
            elif cell_value == "#":
                next_slots[c_idx] = r_idx - 1


def tilt_east(rocks: List[List[str]]) -> None:
    # Stores next column index for each row
    next_slots = [len(rocks[0]) - 1] * len(rocks)
    for c_idx in range(len(rocks[0]) - 1, -1, -1):
        for r_idx in range(len(rocks)):
            cell_value = rocks[r_idx][c_idx]
            if cell_value == "O":
                if next_slots[r_idx] != c_idx:
                    rocks[r_idx][next_slots[r_idx]] = "O"
                    rocks[r_idx][c_idx] = "."

                next_slots[r_idx] -= 1
            elif cell_value == "#":
                next_slots[r_idx] = c_idx - 1


def total_load_on_north(rocks: List[List[str]]) -> int:
    multiplier = len(rocks)
    total = 0
    for row in rocks:
        total += row.count("O") * multiplier
        multiplier -= 1

    return total


def spin_cycle(rocks: List[List[str]]) -> Tuple[int, str]:
    tilt_north(rocks)
    tilt_west(rocks)
    tilt_south(rocks)
    tilt_east(rocks)

    load_on_north = total_load_on_north(rocks)

    return load_on_north, get_rock_data_as_string(rocks)


load_cache: Dict[str, Tuple[int, str, int]] = {}


def compute_total_load(rock_data: str, rocks: List[List[str]], cycle_idx: int) -> Tuple[int, str, int, bool]:
    if rock_data in load_cache:
        load, next_state, first_occurrence = load_cache[rock_data]
        return load, next_state, first_occurrence, True

    load, next_state = spin_cycle(rocks)

    load_cache[rock_data] = load, next_state, cycle_idx
    return load, next_state, cycle_idx, False


class Dish:
    def __init__(self, dish_data: str):
        self.raw_data = dish_data
        self.rock_state = copy.copy(self.raw_data)
        self.rock_matrix: List[List[str]] = []
        self._reset()

    def _reset(self) -> None:
        self.rock_state = copy.copy(self.raw_data)
        self.rock_matrix: List[List[str]] = []
        for r in self.raw_data.split("\n"):
            self.rock_matrix.append([char for char in r])

    def get_total_load(self) -> int:
        self._reset()
        tilt_north(self.rock_matrix)

        return total_load_on_north(self.rock_matrix)

    def get_total_load_after_spin_cycles(self, total_cycles: int) -> int:
        self._reset()
        cycle_index = 1
        first_observed = 1
        total_load = 0
        while cycle_index <= total_cycles:
            total_load, next_rock_state, first_observed, cache_hit = compute_total_load(
                self.rock_state,
                self.rock_matrix,
                cycle_index)

            self.rock_state = next_rock_state

            if cache_hit:
                break

            cycle_index += 1

        print(f"Found repeating cycle at {cycle_index}, first observed at cycle {first_observed}")
        period = cycle_index - first_observed
        print(f"Period of repeating pattern is {period}")

        remainder = (total_cycles - (first_observed - 1)) % period
        print(f"Computing {remainder} remaining cycles")

        # Note: Since we have already advanced to the start of the next repetition group
        # we need to perform 1 less cycle
        for i in range(remainder - 1):
            total_load, next_rock_state, _, _ = compute_total_load(self.rock_state, self.rock_matrix, -1)
            self.rock_state = next_rock_state

        return total_load


file_name = "input_small"
rock_state = pathlib.Path(file_name).read_text().strip()

dish = Dish(rock_state)
print(f"Part 1: {dish.get_total_load()}")
print(f"Part 2: {dish.get_total_load_after_spin_cycles(1000000000)}")
