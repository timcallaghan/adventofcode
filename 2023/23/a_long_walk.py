import pathlib
from enum import Enum
from collections import namedtuple, deque
from typing import List, Set, Optional, Dict

Coords = namedtuple("Coords", "r c")
Edge = namedtuple("Edge", "end_coords distance")


class MapLocation(Enum):
    trail = 0,
    forest = 1
    slope_north = 2,
    slope_east = 3,
    slope_south = 4,
    slope_west = 5


class TrailMap:
    def __init__(self, trail_data: str):
        self.data: List[List[MapLocation]] = []
        for line in trail_data.split("\n"):
            row = []
            for char in line.strip():
                match char:
                    case ".":
                        row.append(MapLocation.trail)
                    case "#":
                        row.append(MapLocation.forest)
                    case "^":
                        row.append(MapLocation.slope_north)
                    case ">":
                        row.append(MapLocation.slope_east)
                    case "v":
                        row.append(MapLocation.slope_south)
                    case "<":
                        row.append(MapLocation.slope_west)

            self.data.append(row)

        self.min_row = 0
        self.max_row = len(self.data)
        self.min_col = 0
        self.max_col = len(self.data[0])
        self.start = Coords(0, 1)
        self.end = Coords(self.max_row - 1, self.max_col - 2)
        self.vertices: Set[Coords] = set()
        self.edges: Dict[Coords, List[Edge]] = {}
        self.visited: Dict[Coords, bool] = {}
        self.longest_path_length = 0
        self.all_slopes: List[MapLocation] = [
            MapLocation.slope_north,
            MapLocation.slope_east,
            MapLocation.slope_south,
            MapLocation.slope_west
        ]
        self._compute_vertices()

    def _north(self, coords: Coords) -> Optional[Coords]:
        return Coords(coords.r - 1, coords.c) if coords.r > self.min_row else None

    def _east(self, coords: Coords) -> Optional[Coords]:
        return Coords(coords.r, coords.c + 1) if coords.c < self.max_col - 1 else None

    def _south(self, coords: Coords) -> Optional[Coords]:
        return Coords(coords.r + 1, coords.c) if coords.r < self.max_row - 1 else None

    def _west(self, coords: Coords) -> Optional[Coords]:
        return Coords(coords.r, coords.c - 1) if coords.c > self.min_col else None

    def _get_location(self, coords: Coords) -> MapLocation:
        return self.data[coords.r][coords.c]

    def _compute_vertices(self) -> None:
        self.vertices.add(self.start)
        self.vertices.add(self.end)
        for r_idx in range(self.max_row):
            for c_idx in range(self.max_col):
                coords = Coords(r_idx, c_idx)
                location = self._get_location(coords)
                if location == MapLocation.forest:
                    continue

                direction_count = 0
                for direction in [self._north(coords), self._east(coords), self._south(coords), self._west(coords)]:
                    if direction and self._get_location(direction) != MapLocation.forest:
                        direction_count += 1

                if direction_count > 2:
                    self.vertices.add(coords)

    def _compute_edges(self, include_slopes: bool) -> None:
        self.edges = {}
        for vertex in self.vertices:
            self.edges[vertex] = []
            edges_from_vertex = deque([Edge(vertex, 0)])
            visited_coords = set()
            while edges_from_vertex:
                coords, distance = edges_from_vertex.popleft()
                if coords in visited_coords:
                    continue

                visited_coords.add(coords)
                if coords in self.vertices and coords != vertex:
                    self.edges[vertex].append(Edge(coords, distance))
                    continue

                coords_location = self._get_location(coords)
                for direction, expected_location in [
                    (self._north(coords), MapLocation.slope_north),
                    (self._east(coords), MapLocation.slope_east),
                    (self._south(coords), MapLocation.slope_south),
                    (self._west(coords), MapLocation.slope_west)
                ]:
                    if not direction:
                        continue

                    direction_location = self._get_location(direction)
                    if direction_location != MapLocation.forest:
                        if include_slopes and coords_location in self.all_slopes \
                                and coords_location != expected_location:
                            continue

                        edges_from_vertex.append(Edge(direction, distance + 1))

    def _traverse_edges_depth_first(self, vertex: Coords, path_length: int):
        if self.visited[vertex]:
            return

        self.visited[vertex] = True
        if vertex == self.end:
            self.longest_path_length = max(self.longest_path_length, path_length)

        for edge in self.edges[vertex]:
            self._traverse_edges_depth_first(edge.end_coords, path_length + edge.distance)

        self.visited[vertex] = False

    def get_longest_path(self, include_slopes: bool) -> int:
        self._compute_edges(include_slopes)
        self.visited = {}
        for v in self.vertices:
            self.visited[v] = False

        self.longest_path_length = 0
        self._traverse_edges_depth_first(self.start, 0)

        return self.longest_path_length


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
trail_map = TrailMap(puzzle_input)

print(f"Part 1: {trail_map.get_longest_path(True)}")
print(f"Part 2: {trail_map.get_longest_path(False)}")
