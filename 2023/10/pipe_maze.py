from typing import List, Self, Dict, Optional
from enum import Enum


class Direction(Enum):
    NORTH = 1,
    EAST = 2,
    SOUTH = 3,
    WEST = 4


opposite_directions: Dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST
}

valid_pipe_joins: Dict[Direction, List[str]] = {
    Direction.NORTH: ["|", "7", "F"],
    Direction.EAST: ["-", "J", "7"],
    Direction.SOUTH: ["|", "L", "J"],
    Direction.WEST: ["-", "L", "F"]
}


class PipeEnds:
    def __init__(self, start: Direction, end: Direction):
        self.start = start
        self.end = end


directions_for_pipe: Dict[str, PipeEnds] = {
    "|": PipeEnds(Direction.SOUTH, Direction.NORTH),
    "-": PipeEnds(Direction.WEST, Direction.EAST),
    "L": PipeEnds(Direction.NORTH, Direction.EAST),
    "7": PipeEnds(Direction.WEST, Direction.SOUTH),
    "J": PipeEnds(Direction.WEST, Direction.NORTH),
    "F": PipeEnds(Direction.SOUTH, Direction.EAST)
}


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"x={self.x}, y = {self.y}"

    def north(self) -> Self:
        return Point(self.x, self.y - 1)

    def east(self) -> Self:
        return Point(self.x + 1, self.y)

    def south(self) -> Self:
        return Point(self.x, self.y + 1)

    def west(self) -> Self:
        return Point(self.x - 1, self.y)

    def is_valid(self, len_x: int, len_y: int) -> bool:
        if 0 <= self.x < len_x and 0 <= self.y < len_y:
            return True

        return False

    def point_for_direction(self, direction: Direction) -> Self:
        match direction:
            case Direction.NORTH:
                return self.north()
            case Direction.EAST:
                return self.east()
            case Direction.SOUTH:
                return self.south()
            case Direction.WEST:
                return self.west()


class Maze:
    def __init__(self):
        self.data: List[List[str]] = []
        self.start = Point(0, 0)
        self.start_pipe = "S"
        self.points_in_loop: List[Point] = []
        self.pipe_verticals: List[List[Point]] = []

    def append_line(self, line_data: str):
        self.data.append([val for val in line_data.strip()])
        start_index = line.find("S")
        if start_index > -1:
            self.start = Point(start_index, len(self.data) - 1)

    def get_pipe_at_point(self, point: Point) -> str:
        if point.x == self.start.x and point.y == self.start.y:
            return self.start_pipe

        return self.data[point.y][point.x]

    def determine_start_pipe(self):
        north = self.start.north()
        east = self.start.east()
        south = self.start.south()
        west = self.start.west()

        connects_to_north = self.get_pipe_at_point(north) in valid_pipe_joins[Direction.NORTH]
        connects_to_east = self.get_pipe_at_point(east) in valid_pipe_joins[Direction.EAST]
        connects_to_south = self.get_pipe_at_point(south) in valid_pipe_joins[Direction.SOUTH]
        connects_to_west = self.get_pipe_at_point(west) in valid_pipe_joins[Direction.WEST]

        if connects_to_north and connects_to_east:
            self.start_pipe = "L"
        elif connects_to_north and connects_to_south:
            self.start_pipe = "|"
        elif connects_to_north and connects_to_west:
            self.start_pipe = "J"
        elif connects_to_east and connects_to_south:
            self.start_pipe = "F"
        elif connects_to_east and connects_to_west:
            self.start_pipe = "-"
        elif connects_to_south and connects_to_west:
            self.start_pipe = "7"

        print(f"{self.start_pipe=}")

    def get_next_direction(self, existing_points: List[Point], previous_direction: Direction) -> Direction:
        last_point = existing_points[-1]
        last_pipe = self.get_pipe_at_point(last_point)
        directions = directions_for_pipe[last_pipe]
        next_direction = directions.start
        if directions.end != previous_direction:
            next_direction = directions.end

        return next_direction

    def is_point_in_loop(self, x: int, y: int) -> bool:
        for p in self.points_in_loop:
            if p.x == x and p.y == y:
                return True

        return False

    def is_point_in_verticals(self, x: int, y: int) -> bool:
        for p in self.pipe_verticals[y]:
            if p.x == x:
                return True
        return False

    def visualise_pipe_loop(self):
        visualisation: List[str] = []
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                if self.is_point_in_loop(x, y):
                    visualisation.append("*")
                else:
                    visualisation.append(".")

            visualisation.append("\n")

        print(''.join(visualisation))

    def traverse_loop(self) -> int:
        forwards_points: List[Point] = [self.start]
        backwards_points: List[Point] = [self.start]

        start_directions = directions_for_pipe[self.start_pipe]
        previous_forwards = start_directions.start
        previous_backwards = start_directions.end

        while True:
            next_forward_direction = self.get_next_direction(forwards_points, previous_forwards)
            next_backward_direction = self.get_next_direction(backwards_points, previous_backwards)

            next_forward_point = forwards_points[-1].point_for_direction(next_forward_direction)
            forwards_points.append(next_forward_point)
            next_backward_point = backwards_points[-1].point_for_direction(next_backward_direction)
            backwards_points.append(next_backward_point)

            if next_forward_point.x == next_backward_point.x and next_forward_point.y == next_backward_point.y:
                break

            previous_forwards = opposite_directions[next_forward_direction]
            previous_backwards = opposite_directions[next_backward_direction]

        self.points_in_loop.extend(forwards_points)
        backwards_points.reverse()
        self.points_in_loop.extend(backwards_points[1:])
        return len(forwards_points) - 1

    def determine_pipe_verticals(self):
        for y in range(len(self.data)):
            self.pipe_verticals.append([])
            segment_start: Optional[Point] = None
            segment_start_pipe = ""
            for x in range(len(self.data[0])):
                if self.is_point_in_loop(x, y):
                    current_point = Point(x, y)
                    pipe = self.get_pipe_at_point(current_point)
                    if pipe == "|":
                        self.pipe_verticals[y].append(current_point)
                    else:
                        if segment_start is None:
                            segment_start = current_point
                            segment_start_pipe = pipe
                        else:
                            if pipe == "-":
                                continue
                            else:
                                match pipe:
                                    case "J":
                                        if segment_start_pipe == "F":
                                            self.pipe_verticals[y].append(current_point)
                                    case "7":
                                        if segment_start_pipe == "L":
                                            self.pipe_verticals[y].append(current_point)

                                segment_start = None
                                segment_start_pipe = ""

    # This uses https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
    # Essentially, given a point not on the loop we calculate the number of pipe intersections to the right
    # If the number of intersections is odd then the point is inside the loop.
    def get_points_inside_loop(self):
        points_inside = 0
        max_x = len(self.data[0])
        for y in range(len(self.data)):
            for x in range(max_x):
                if self.is_point_in_loop(x, y):
                    continue

                pipes_to_right = 0
                if x < max_x - 1:
                    for right_x in range(x + 1, max_x):
                        if self.is_point_in_verticals(right_x, y):
                            pipes_to_right += 1

                if pipes_to_right % 2 == 1:
                    points_inside += 1

        return points_inside


maze: Maze = Maze()
file_name = "input_small"

with open(file_name, encoding="utf-8") as f:
    for line in f:
        maze.append_line(line)

maze.determine_start_pipe()
print(f"Part 1: {maze.traverse_loop()}")

# Visualisation of the pipe loop
maze.visualise_pipe_loop()
maze.determine_pipe_verticals()
print(f"Part 2: {maze.get_points_inside_loop()}")
