import pathlib
from typing import List, Dict, Optional
from collections import namedtuple
from enum import IntEnum
import heapq


class Direction(IntEnum):
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4
    NONE = 5


Point = namedtuple("Point", "r c")
PointHistory = namedtuple("PointHistory", "point direction steps_in_direction")
CostPointHistory = namedtuple("CostPointHistory", "cost point_history")


class CityMap:
    def __init__(self, map_data: str):
        self.blocks: List[List[int]] = []
        for r in map_data.split():
            block_row = [int(b) for b in r]
            self.blocks.append(block_row)

        self.min_row = 0
        self.max_row = len(self.blocks)
        self.min_col = 0
        self.max_col = len(self.blocks[0])
        self.start = Point(0, 0)
        self.end = Point(self.max_row - 1, self.max_col - 1)
        self.all_directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

    def _cost_at_point(self, point: Point) -> int:
        return self.blocks[point.r][point.c]

    def _north(self, point: Point) -> Optional[Point]:
        return Point(point.r - 1, point.c) if point.r > self.min_row else None

    def _east(self, point: Point) -> Optional[Point]:
        return Point(point.r, point.c + 1) if point.c < self.max_col - 1 else None

    def _south(self, point: Point) -> Optional[Point]:
        return Point(point.r + 1, point.c) if point.r < self.max_row - 1 else None

    def _west(self, point: Point) -> Optional[Point]:
        return Point(point.r, point.c - 1) if point.c > self.min_col else None

    def _point_in_direction(self, point: Point, direction: Direction) -> Optional[Point]:
        match direction:
            case Direction.NORTH:
                return self._north(point)
            case Direction.EAST:
                return self._east(point)
            case Direction.SOUTH:
                return self._south(point)
            case Direction.WEST:
                return self._west(point)

    @staticmethod
    def _opposite_direction(direction: Direction) -> Direction:
        match direction:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.SOUTH:
                return Direction.NORTH
            case Direction.WEST:
                return Direction.EAST
            case Direction.NONE:
                return Direction.NONE

    def _get_directions_from_point(self,
                                   point_history: PointHistory,
                                   apply_extra_constraints: bool) -> List[PointHistory]:
        valid_directions = []

        opposite_direction = self._opposite_direction(point_history.direction)
        for direction in self.all_directions:
            if direction == opposite_direction:
                continue

            new_point = self._point_in_direction(point_history.point, direction)
            if new_point:
                steps = 1 if point_history.direction != direction else point_history.steps_in_direction + 1
                if apply_extra_constraints:
                    if point_history.direction != direction and 1 <= point_history.steps_in_direction < 4:
                        continue

                    if steps <= 10:
                        valid_directions.append(PointHistory(new_point, direction, steps))

                elif steps <= 3:
                    valid_directions.append(PointHistory(new_point, direction, steps))

        return valid_directions

    def get_minimum_heat_loss(self, apply_extra_constraints: bool) -> int:
        point_history_cost_cache: Dict[PointHistory, int] = {}
        points_to_process = [CostPointHistory(0, PointHistory(self.start, Direction.NONE, 0))]
        heapq.heapify(points_to_process)

        while points_to_process:
            cost, point_history = heapq.heappop(points_to_process)
            if point_history in point_history_cost_cache:
                continue

            point_history_cost_cache[point_history] = cost
            for next_point_history in self._get_directions_from_point(point_history, apply_extra_constraints):
                if next_point_history in point_history_cost_cache:
                    continue

                total_cost_at_point = cost + self._cost_at_point(next_point_history.point)
                heapq.heappush(points_to_process, CostPointHistory(total_cost_at_point, next_point_history))

        # Upper bound on the minimum is if every block contained 9
        minimum_heat_loss = 9 * (self.max_row + self.max_col - 1)
        for point_history, cost in point_history_cost_cache.items():
            if (point_history.point == self.end
                    and (not apply_extra_constraints or point_history.steps_in_direction >= 4)):
                minimum_heat_loss = min(minimum_heat_loss, cost)

        return minimum_heat_loss


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
city_map = CityMap(puzzle_input)

print(f"Part 1: {city_map.get_minimum_heat_loss(False)}")
print(f"Part 2: {city_map.get_minimum_heat_loss(True)}")
