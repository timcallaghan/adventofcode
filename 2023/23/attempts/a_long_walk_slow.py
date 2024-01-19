import pathlib
from typing import List
from collections import OrderedDict
from enum import Enum
import copy
import sys


class MapLocation(Enum):
    trail = 0,
    forest = 1
    slope_north = 2,
    slope_east = 3,
    slope_south = 4,
    slope_west = 5


class TrailMap:
    def __init__(self, map_data: str):
        self.raw_data = map_data
        self.data: List[List[MapLocation]] = []

        for line in map_data.split("\n"):
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

        self.max_row = len(self.data)
        self.max_col = len(self.data[0])
        self.start = "0:1"
        self.end = f"{self.max_row-1}:{self.max_col-2}"
        self.dead_end = "-1:-1"
        self.see_other = "see_other"

    def __get_next_locations(self,
                             current_location: str,
                             path: OrderedDict[str, str],
                             ignore_slopes: bool) -> List[str]:
        c_row, c_col = [int(char) for char in current_location.split(":")]
        current_coords = self.data[c_row][c_col]
        if ignore_slopes and current_coords != MapLocation.forest:
            current_coords = MapLocation.trail

        cardinal_directions: List[str] = []

        if c_row > 0 \
                and (current_coords == MapLocation.trail or current_coords == MapLocation.slope_north):
            north = self.data[c_row-1][c_col]
            if ignore_slopes and north != MapLocation.forest:
                north = MapLocation.trail

            north_coords = f"{c_row - 1}:{c_col}"
            if north != MapLocation.slope_south and north_coords not in path and north != MapLocation.forest:
                cardinal_directions.append(north_coords)

        if c_col < self.max_col - 1 \
                and (current_coords == MapLocation.trail or current_coords == MapLocation.slope_east):
            east = self.data[c_row][c_col + 1]
            if ignore_slopes and east != MapLocation.forest:
                east = MapLocation.trail

            east_coords = f"{c_row}:{c_col + 1}"
            if east != MapLocation.slope_west and east_coords not in path and east != MapLocation.forest:
                cardinal_directions.append(east_coords)

        if c_row < self.max_row - 1 \
                and (current_coords == MapLocation.trail or current_coords == MapLocation.slope_south):
            south = self.data[c_row + 1][c_col]
            if ignore_slopes and south != MapLocation.forest:
                south = MapLocation.trail

            south_coords = f"{c_row + 1}:{c_col}"
            if south != MapLocation.slope_north and south_coords not in path and south != MapLocation.forest:
                cardinal_directions.append(south_coords)

        if c_col > 0 \
                and (current_coords == MapLocation.trail or current_coords == MapLocation.slope_west):
            west = self.data[c_row][c_col - 1]
            if ignore_slopes and west != MapLocation.forest:
                west = MapLocation.trail

            west_coords = f"{c_row}:{c_col - 1}"
            if west != MapLocation.slope_east and west_coords not in path and west != MapLocation.forest:
                cardinal_directions.append(west_coords)

        return cardinal_directions

    def __explore_paths(self, paths: List[OrderedDict[str, str]], ignore_slopes: bool) -> None:
        path_splits = []
        has_paths_to_explore = False
        for p in paths:
            current_location = next(reversed(p))
            if (current_location == self.end
                    or current_location == self.dead_end
                    or current_location == self.see_other):
                continue

            has_paths_to_explore = True
            next_locations = self.__get_next_locations(current_location, p, ignore_slopes)

            if len(next_locations) > 0:
                for idx in range(len(next_locations) - 1, -1, -1):
                    location_split = next_locations[idx]

                    if location_split == self.end:
                        if idx == 0:
                            p[location_split] = current_location
                        else:
                            new_path = copy.deepcopy(p)
                            new_path[location_split] = current_location
                            path_splits.append(new_path)
                    else:
                        is_in_other_path = False
                        for p_alt in paths:
                            if p_alt == p:
                                continue
                            if location_split in p_alt:
                                is_in_other_path = True
                                if idx == 0:
                                    p[self.see_other] = location_split
                                else:
                                    new_path = copy.deepcopy(p)
                                    new_path[self.see_other] = location_split
                                    path_splits.append(new_path)

                        if not is_in_other_path:
                            if idx == 0:
                                p[location_split] = current_location
                            else:
                                new_path = copy.deepcopy(p)
                                new_path[location_split] = current_location
                                path_splits.append(new_path)
            else:
                p[self.dead_end] = current_location

        if has_paths_to_explore:
            paths.extend(path_splits)
            self.__explore_paths(paths, ignore_slopes)

    def __visualise_path(self, path: OrderedDict[str, str]) -> None:
        for r in range(self.max_row):
            line = ""
            for c in range(self.max_col):
                if f"{r}:{c}" == self.start:
                    line += "S"
                elif f"{r}:{c}" in path:
                    line += "O"
                else:
                    char = ""
                    location = self.data[r][c]
                    match location:
                        case MapLocation.trail:
                            char = "."
                        case MapLocation.forest:
                            char = "#"
                        case MapLocation.slope_north:
                            char = "^"
                        case MapLocation.slope_east:
                            char = ">"
                        case MapLocation.slope_south:
                            char = "v"
                        case MapLocation.slope_west:
                            char = "<"
                    line += char
            print(line)

    def get_longest_hike(self, ignore_slopes: bool, visualise: bool) -> int:
        sys.setrecursionlimit(6000)
        start_path = OrderedDict()
        start_path[self.start] = self.start
        # Each path is an ordered dictionary where the key is the location
        # and the value is the previous location
        paths: List[OrderedDict[str, str]] = [start_path]

        self.__explore_paths(paths, ignore_slopes)

        longest_path_length = 0
        longest_path = None
        for p in paths:
            final_location = next(reversed(p))
            print(final_location)
            if final_location == self.end and len(p) - 1 > longest_path_length:
                longest_path_length = len(p) - 1
                longest_path = p

        if visualise:
            self.__visualise_path(longest_path)

        return longest_path_length


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
tm = TrailMap(puzzle_input)

print(f"Part 1: {tm.get_longest_hike(False, False)}")
print(f"Part 2: {tm.get_longest_hike(True, False)}")
