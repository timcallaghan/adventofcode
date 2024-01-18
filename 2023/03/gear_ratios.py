from enum import Enum
from typing import Optional, Self, List, Dict


class LocationType(Enum):
    SYMBOL = 1,
    NUMBER = 2


class Location:
    def __init__(self, row: int, col: int, location_type: LocationType, char: str):
        self.row = row
        self.start_col = col
        self.end_col = col
        self.location_type = location_type
        self.value = char

    def expand(self, char: str):
        self.end_col += 1
        self.value += char

    def is_adjacent_to_symbol(self, symbol_location: Self) -> bool:
        if self.location_type == symbol_location.location_type:
            return False

        for row in range(self.row - 1, self.row + 2):
            for col in range(self.start_col - 1, self.end_col + 2):
                if symbol_location.row == row and symbol_location.start_col == col:
                    return True

        return False

    def is_gear_candidate(self) -> bool:
        return self.value == "*"

    def gear_key(self) -> str:
        if self.location_type == LocationType.SYMBOL and self.value == "*":
            return f"{self.row}:{self.start_col}"

        return ""

    def __str__(self):
        return f"{self.row=} {self.start_col=} {self.end_col=} {self.value=}"


class GearCandidate:
    def __init__(self, location: Location):
        self.location = location
        self.adjacent_parts: List[Location] = []

    def add_part(self, part_location: Location):
        self.adjacent_parts.append(part_location)

    def is_gear(self) -> bool:
        return len(self.adjacent_parts) == 2

    def gear_ratio(self) -> int:
        if self.is_gear():
            return int(self.adjacent_parts[0].value) * int(self.adjacent_parts[1].value)

        return 0


def print_all_lines(lines: list):
    for li in lines:
        print(li)


all_lines = []
file_name = "input_small"
with open(file_name, encoding="utf-8") as f:
    for line in f:
        all_lines.append(line.strip())

# print_all_lines(all_lines)
line_count = len(all_lines)
line_width = len(all_lines[0])

number_locations = []
symbol_locations = []

current_location: Optional[Location] = None
for r in range(line_count):
    for c in range(line_width):
        current_char = all_lines[r][c]
        if current_char == ".":
            if current_location is not None:
                match current_location.location_type:
                    case LocationType.SYMBOL:
                        symbol_locations.append(current_location)
                    case LocationType.NUMBER:
                        number_locations.append(current_location)

                current_location = None
        elif current_char.isdigit():
            if current_location is None:
                current_location = Location(r, c, LocationType.NUMBER, current_char)
            elif current_location.location_type == LocationType.SYMBOL:
                symbol_locations.append(current_location)
                current_location = Location(r, c, LocationType.NUMBER, current_char)
            else:
                current_location.expand(current_char)
        else:
            if current_location is None:
                current_location = Location(r, c, LocationType.SYMBOL, current_char)
            elif current_location.location_type == LocationType.NUMBER:
                number_locations.append(current_location)
                current_location = Location(r, c, LocationType.SYMBOL, current_char)
            else:
                symbol_locations.append(current_location)
                current_location = Location(r, c, LocationType.SYMBOL, current_char)

    if current_location is not None:
        if current_location.location_type == LocationType.SYMBOL:
            symbol_locations.append(current_location)
        else:
            number_locations.append(current_location)

        current_location = None

part_number_locations: List[Location] = []
gear_candidates: Dict[str, GearCandidate] = {}
for loc in number_locations:
    for sym_loc in symbol_locations:
        if loc.is_adjacent_to_symbol(sym_loc):
            part_number_locations.append(loc)

            if sym_loc.is_gear_candidate():
                if sym_loc.gear_key() not in gear_candidates:
                    gear_candidates[sym_loc.gear_key()] = GearCandidate(sym_loc)

                gear_candidates[sym_loc.gear_key()].add_part(loc)

print(f"Part 1: {sum([int(part_num.value) for part_num in part_number_locations])}")

sum_gear_ratios: int = 0
for gear_key in gear_candidates:
    gear_candidate = gear_candidates[gear_key]
    if gear_candidate.is_gear():
        sum_gear_ratios += gear_candidate.gear_ratio()

print(f"Part 2: {sum_gear_ratios}")
