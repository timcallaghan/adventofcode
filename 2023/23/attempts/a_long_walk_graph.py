import pathlib
from enum import Enum
from typing import List, Optional, Self, Dict, Set
from collections import OrderedDict
import sys


is_logging = True


def log(info: str):
    if is_logging:
        print(info)


class MapLocation(Enum):
    trail = 0,
    forest = 1
    slope_north = 2,
    slope_east = 3,
    slope_south = 4,
    slope_west = 5


class Coord:
    def __init__(self, r:int, c: int):
        self._r = r
        self._c = c
        self._id = f"{r}:{c}"

    def __eq__(self, other):
        if not isinstance(other, Coord):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    @property
    def r(self) -> int:
        return self._r

    @property
    def c(self) -> int:
        return self._c

    @property
    def id(self) -> str:
        return self._id


class PathSegment:
    def __init__(self, start: Coord, direction: Coord):
        self._start = start
        self._direction = direction
        self._coords: OrderedDict[Coord, None] = OrderedDict()
        self._coords[start] = None
        self._coords[direction] = None
        self._id = f"{self._start.id}|{self._direction.id}"

    def __eq__(self, other):
        if not isinstance(other, PathSegment):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def extend(self, coord: Coord) -> None:
        self._coords[coord] = None

    def contains(self, coord: Coord) -> bool:
        return coord in self._coords

    @property
    def start(self) -> Coord:
        return self._start

    @property
    def direction(self) -> Coord:
        return self._direction

    @property
    def end(self) -> Coord:
        return next(reversed(self._coords.keys()))

    @property
    def length(self):
        return len(self._coords) - 1

    def get_reversed(self) -> Self:
        start = None
        direction = None
        reversed_segment = None
        for c in reversed(self._coords.keys()):
            if not start:
                start = c
            elif not direction:
                direction = c
                reversed_segment = PathSegment(start, direction)
            else:
                reversed_segment.extend(c)

        return reversed_segment

    @property
    def coords(self) -> List[Coord]:
        return list(self._coords.keys())


class Path:
    def __init__(self, path_segment: PathSegment):
        self._segments: OrderedDict[PathSegment, None] = OrderedDict()
        self._segments[path_segment] = None
        self._is_dead_end = False

    def extend(self, path_segment: PathSegment) -> None:
        self._segments[path_segment] = None

    def contains(self, path_segment: PathSegment) -> bool:
        # This needs to be better - we need to consider all coords in the segment except the end, not just the start
        if path_segment in self._segments:
            return True

        for ps in self._segments.keys():
            if path_segment.start == ps.start or path_segment.start == path_segment.end:
                return True

        for coord in path_segment.coords[0:-2]:
            for ps in self._segments.keys():
                if ps.contains(coord):
                    return True

        return False

    def is_equal_to(self, other: Self) -> bool:
        if len(self._segments) == len(other._segments):
            self_keys = list(self._segments.keys())
            other_keys = list(other._segments.keys())
            for idx in range(len(self_keys)):
                if self_keys[idx] != other_keys[idx]:
                    return False

            return True

        return False

    @property
    def id(self) -> str:
        path_str = ""
        for ps in reversed(self._segments):
            if path_str == "":
                path_str = f"{ps.start.id}->{ps.end.id}"
            else:
                path_str += f"->{ps.end.id}"

        return path_str

    @property
    def length(self) -> int:
        path_length = 0
        for ps in self._segments:
            path_length += ps.length

        return path_length

    @property
    def start(self) -> Coord:
        return next(reversed(self._segments)).start

    @property
    def is_dead_end(self) -> bool:
        return self._is_dead_end

    def set_dead_end(self) -> None:
        self._is_dead_end = True

    def duplicate(self) -> Self:
        path_copy = None
        for ps in iter(self._segments):
            if not path_copy:
                path_copy = Path(ps)
            else:
                path_copy.extend(ps)

        return path_copy


class TrailMapGraph:
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
        self.start = Coord(0, 1)
        self.end = Coord(self.max_row-1, self.max_col-2)
        self.path_segments: Set[PathSegment] = set()
        self.path_segment_end: Dict[Coord, List[PathSegment]] = {}

    def _north(self, coord: Coord) -> Optional[Coord]:
        return Coord(coord.r - 1, coord.c) if coord.r > self.min_row else None

    def _east(self, coord: Coord) -> Optional[Coord]:
        return Coord(coord.r, coord.c + 1) if coord.c < self.max_col - 1 else None

    def _south(self, coord: Coord) -> Optional[Coord]:
        return Coord(coord.r + 1, coord.c) if coord.r < self.max_row - 1 else None

    def _west(self, coord: Coord) -> Optional[Coord]:
        return Coord(coord.r, coord.c - 1) if coord.c > self.min_col else None

    def _get_location(self, coords: Coord) -> MapLocation:
        return self.data[coords.r][coords.c]

    def _get_exploration_directions(self, path_segment: PathSegment, ignore_slopes: bool) -> List[Coord]:
        coords = []
        current_coords = path_segment.end
        current_location = self._get_location(current_coords)

        north = self._north(current_coords)
        if north and not path_segment.contains(north):
            ml = self._get_location(north)
            if (ignore_slopes or ml != MapLocation.slope_south) and ml != MapLocation.forest:
                if current_location == MapLocation.trail or ignore_slopes or current_location == MapLocation.slope_north:
                    coords.append(north)

        east = self._east(current_coords)
        if east and not path_segment.contains(east):
            ml = self._get_location(east)
            if (ignore_slopes or ml != MapLocation.slope_west) and ml != MapLocation.forest:
                if current_location == MapLocation.trail or ignore_slopes or current_location == MapLocation.slope_east:
                    coords.append(east)

        south = self._south(current_coords)
        if south and not path_segment.contains(south):
            ml = self._get_location(south)
            if (ignore_slopes or ml != MapLocation.slope_north) and ml != MapLocation.forest:
                if current_location == MapLocation.trail or ignore_slopes or current_location == MapLocation.slope_south:
                    coords.append(south)

        west = self._west(current_coords)
        if west and not path_segment.contains(west):
            ml = self._get_location(west)
            if (ignore_slopes or ml != MapLocation.slope_east) and ml != MapLocation.forest:
                if current_location == MapLocation.trail or ignore_slopes or current_location == MapLocation.slope_west:
                    coords.append(west)

        return coords

    def _add_path_segment_end(self, path_segment: PathSegment) -> None:
        if path_segment.end not in self.path_segment_end:
            self.path_segment_end[path_segment.end] = []

        self.path_segment_end[path_segment.end].append(path_segment)

    def _explore_path_segments(self, path_segment: PathSegment, ignore_slopes: bool) -> None:
        directions = self._get_exploration_directions(path_segment, ignore_slopes)
        dir_count = len(directions)
        if dir_count == 0:
            self._add_path_segment_end(path_segment)
        elif dir_count == 1:
            path_segment.extend(directions[0])
            self._explore_path_segments(path_segment, ignore_slopes)
        else:
            self._add_path_segment_end(path_segment)
            if ignore_slopes:
                reversed_path_segment = path_segment.get_reversed()
                if reversed_path_segment not in self.path_segments:
                    self.path_segments.add(reversed_path_segment)
                    self._add_path_segment_end(reversed_path_segment)

            for direction in directions:
                next_path_segment = PathSegment(path_segment.end, direction)
                if next_path_segment not in self.path_segments:
                    self.path_segments.add(next_path_segment)
                    self._explore_path_segments(next_path_segment, ignore_slopes)

    def _get_paths_from_start_to_end(self) -> List[Path]:
        longest_path = 0
        paths: List[Path] = [Path(ps) for ps in self.path_segment_end[self.end]]
        while True:
            should_continue = False
            new_paths = []
            for p in paths:
                if p.is_dead_end or p.start == self.start:
                    continue

                previous_segments = self.path_segment_end[p.start]
                previous_segment_count = len(previous_segments)
                if previous_segment_count == 0:
                    p.set_dead_end()
                elif previous_segment_count > 0:
                    for ps_idx in range(1, previous_segment_count):
                        previous_segment = previous_segments[ps_idx]
                        if not p.contains(previous_segment):
                            should_continue = True
                            path_copy = p.duplicate()
                            path_copy.extend(previous_segment)
                            new_paths.append(path_copy)

                    if not p.contains(previous_segments[0]):
                        should_continue = True
                        p.extend(previous_segments[0])
                        if previous_segments[0].start == self.start:
                            print(f"Valid path found (length={p.length}): {p.id}")
                            if longest_path < p.length:
                                longest_path = p.length
                                print(f"New longest path found: {longest_path}")
                    else:
                        p.set_dead_end()

            if not should_continue:
                break

            for np in new_paths:
                should_add = True
                for p in paths:
                    if p.is_equal_to(np):
                        should_add = False
                        break

                if should_add:
                    paths.append(np)

        valid_paths = []
        for p in paths:
            if p.start == self.start:
                valid_paths.append(p)

        return valid_paths

    def get_longest_directed_hike(self) -> int:
        self.path_segments = set()
        start_path_segment = PathSegment(self.start, self._south(self.start))
        self.path_segments.add(start_path_segment)
        self._explore_path_segments(start_path_segment, False)

        paths = self._get_paths_from_start_to_end()

        longest_hike = 0
        for p in paths:
            path_length = p.length
            if path_length > longest_hike:
                longest_hike = path_length

        return longest_hike

    def get_longest_hike(self) -> int:
        self.path_segments = set()
        start_path_segment = PathSegment(self.start, self._south(self.start))
        self.path_segments.add(start_path_segment)
        self._explore_path_segments(start_path_segment, True)

        paths = self._get_paths_from_start_to_end()

        longest_hike = 0
        for p in paths:
            path_length = p.length
            if path_length > longest_hike:
                longest_hike = path_length

        return longest_hike


sys.setrecursionlimit(8000)
file_name = "input"
puzzle_input = pathlib.Path(file_name).read_text().strip()
tmg = TrailMapGraph(puzzle_input)

#print(f"Part 1: {tmg.get_longest_directed_hike()}")
print(f"Part 2: {tmg.get_longest_hike()}")
