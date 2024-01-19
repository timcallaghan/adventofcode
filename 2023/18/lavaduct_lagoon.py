import pathlib
from collections import namedtuple
from typing import List, Tuple


Point = namedtuple("Point", "x y")


class Lagoon:
    def __init__(self, dig_plan_data: str):
        self.raw_data = dig_plan_data
        self.vertices: List[Point] = []
        self.perimeter_length: int = 0
        self.area: int = 0

    @staticmethod
    def _get_next_point_and_distance(move_data: str, point: Point, use_hex: bool) -> Tuple[Point, int]:
        move_data = move_data.replace("(#", "").replace(")", "")
        direction, dist, hex_str = move_data.split(" ")

        distance = int(dist)
        if use_hex:
            distance = int(hex_str[0:-1], 16)
            match int(hex_str[-1]):
                case 0:
                    direction = "R"
                case 1:
                    direction = "D"
                case 2:
                    direction = "L"
                case 3:
                    direction = "U"

        next_x = point.x
        next_y = point.y
        match direction:
            case "U":
                next_y += distance
            case "R":
                next_x += distance
            case "D":
                next_y -= distance
            case "L":
                next_x -= distance

        return Point(next_x, next_y), distance

    def _compute_polygon_data(self, use_hex: bool) -> None:
        self.vertices = []
        self.perimeter_length = 0

        current_point = Point(0, 0)
        self.vertices.append(current_point)
        for line in self.raw_data.split("\n"):
            current_point, distance = self._get_next_point_and_distance(line, current_point, use_hex)
            self.vertices.append(current_point)
            self.perimeter_length += distance

        double_area = 0
        for idx in range(0, len(self.vertices) - 1):
            p1 = self.vertices[idx]
            p2 = self.vertices[idx + 1]

            double_area += p1.x * p2.y - p1.y * p2.x

        self.area = abs(double_area)//2 + self.perimeter_length//2 + 1

    def compute_area(self, use_hex: bool) -> int:
        self._compute_polygon_data(use_hex)
        return self.area


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
lagoon = Lagoon(puzzle_input)

print(f"Part 1: {lagoon.compute_area(False)}")
print(f"Part 2: {lagoon.compute_area(True)}")
