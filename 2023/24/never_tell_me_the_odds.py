import pathlib
from typing import List, Self, Optional, Tuple
from z3 import *

should_log = False


def log(data: str):
    if should_log:
        print(data)


class Point:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class Line:
    def __init__(self, line_data: str):
        self.raw_data = line_data

        point, _, vector = line_data.partition("@")
        x, y, z = point.strip().split(",")
        self.x1 = int(x)
        self.y1 = int(y)
        self.z1 = int(z)

        u_val, v_val, w_val = vector.strip().split(",")
        self.u = int(u_val)
        self.v = int(v_val)
        self.w = int(w_val)

        self.m = self.v / self.u

        self.x2 = self.x1 + self.u
        self.y2 = self.y1 + self.v
        self.z2 = self.z1 + self.w

    def is_slope_valid(self) -> bool:
        return self.u != 0 and self.v != 0 and self.w != 0

    def are_slopes_equal(self, other: Self) -> bool:
        return self.v * other.u == other.v * self.u

    def are_intercepts_equal(self, other: Self) -> bool:
        intercept = other.u * (self.y1 * self.u - self.v * self.x1)
        other_intercept = self.u * (other.y1 * other.u - other.v * other.x1)
        return intercept == other_intercept

    def is_collinear_with(self, other: Self) -> bool:
        return self.are_slopes_equal(other) and self.are_intercepts_equal(other)

    def y(self, x: int) -> float:
        return self.y1 + self.m * (x - self.x1)

    def get_intersection_point(self, other: Self) -> Tuple[bool, Optional[Point]]:
        if self.is_collinear_with(other):
            log(f"{self.raw_data} is collinear to {other.raw_data} - infinite intersections")
            return True, None

        if self.are_slopes_equal(other):
            log(f"{self.raw_data} is parallel to {other.raw_data} - no intersection")
            return False, None

        # Using https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        denominator = (self.x1 - self.x2) * (other.y1 - other.y2) - (self.y1 - self.y2) * (other.x1 - other.x2)

        numerator_x = (self.x1 * self.y2 - self.y1 * self.x2) * (other.x1 - other.x2)
        numerator_x -= (self.x1 - self.x2) * (other.x1 * other.y2 - other.y1 * other.x2)

        numerator_y = (self.x1 * self.y2 - self.y1 * self.x2) * (other.y1 - other.y2)
        numerator_y -= (self.y1 - self.y2) * (other.x1 * other.y2 - other.y1 * other.x2)

        return True, Point(numerator_x / denominator, numerator_y / denominator, 0)

    def is_in_future(self, x_val: float) -> bool:
        return (self.u > 0 and self.x1 < x_val) or (self.u < 0 and self.x1 > x_val)


class Hailstones:
    def __init__(self, hailstone_data: str):
        self.hailstones: List[Line] = []
        for line_data in hailstone_data.strip().split("\n"):
            line = Line(line_data)
            self.hailstones.append(line)
            if not line.is_slope_valid():
                print(f"Invalid line with data {line_data}")

    @staticmethod
    def __does_intersect_in_future_space(h1: Line, f_h2: Line, min_xy: int, max_xy: int) -> bool:
        intersects, intersection_point = h1.get_intersection_point(f_h2)
        if not intersects:
            return False

        if not intersection_point:
            # Collinear
            log(f"{h1.raw_data} is collinear with {f_h2.raw_data}")
            return h1.is_in_future(min_xy) \
                and h1.is_in_future(max_xy) \
                and h1.y(min_xy) >= min_xy \
                and h1.y(max_xy) <= max_xy
        else:
            if not h1.is_in_future(intersection_point.x):
                log((f"Intersection point x={intersection_point.x}, y={intersection_point.y} is"
                     f" in the past for {h1.raw_data}"))
                return False

            if not f_h2.is_in_future(intersection_point.x):
                log((f"Intersection point x={intersection_point.x}, y={intersection_point.y} is"
                     f" in the past for {f_h2.raw_data}"))
                return False

            if min_xy <= intersection_point.x <= max_xy and min_xy <= intersection_point.y <= max_xy:
                log((f"Intersection point x={intersection_point.x}, y={intersection_point.y} is"
                    f"inside {min_xy}-{max_xy}"))
                return True

            log((f"Intersection point x={intersection_point.x}, y={intersection_point.y} is"
                 f"outside {min_xy}-{max_xy}"))
            return False

    def get_intersections(self, min_xy: int, max_xy: int) -> int:
        intersections = 0
        for h1_idx in range(len(self.hailstones)):
            for f_h2_idx in range(h1_idx + 1, len(self.hailstones)):
                h1 = self.hailstones[h1_idx]
                f_h2 = self.hailstones[f_h2_idx]

                if self.__does_intersect_in_future_space(h1, f_h2, min_xy, max_xy):
                    intersections += 1

        return intersections

    def get_coords_metric_for_line_intersecting_all_hailstones(self) -> int:
        # Since lines are all skew, we only need consider 3 lines to determine the line on the regulus that
        # traverses all skew lines (arbitrarily choose the first 3 hailstones)
        f_h1 = self.hailstones[0]
        f_h2 = self.hailstones[1]
        f_h3 = self.hailstones[2]

        f_x = Real("x")
        f_y = Real("y")
        f_z = Real("z")
        f_u = Real("u")
        f_v = Real("v")
        f_w = Real("w")
        f_t1 = Real("t1")
        f_t2 = Real("t2")
        f_t3 = Real("t3")

        solver = Solver()
        solver.add(f_h1.x1 + f_t1 * f_h1.u - f_x - f_t1 * f_u == 0)
        solver.add(f_h1.y1 + f_t1 * f_h1.v - f_y - f_t1 * f_v == 0)
        solver.add(f_h1.z1 + f_t1 * f_h1.w - f_z - f_t1 * f_w == 0)

        solver.add(f_h2.x1 + f_t2 * f_h2.u - f_x - f_t2 * f_u == 0)
        solver.add(f_h2.y1 + f_t2 * f_h2.v - f_y - f_t2 * f_v == 0)
        solver.add(f_h2.z1 + f_t2 * f_h2.w - f_z - f_t2 * f_w == 0)

        solver.add(f_h3.x1 + f_t3 * f_h3.u - f_x - f_t3 * f_u == 0)
        solver.add(f_h3.y1 + f_t3 * f_h3.v - f_y - f_t3 * f_v == 0)
        solver.add(f_h3.z1 + f_t3 * f_h3.w - f_z - f_t3 * f_w == 0)

        res = solver.check()
        print(res)
        model = solver.model()

        x = model.eval(f_x)
        y = model.eval(f_y)
        z = model.eval(f_z)
        u = model.eval(f_u)
        v = model.eval(f_v)
        w = model.eval(f_w)
        t1 = model.eval(f_t1)
        t2 = model.eval(f_t2)
        t3 = model.eval(f_t3)

        print(f"{x=}, {y=}, {z=}, {u=}, {v=}, {w=}, {t1=}, {t2=}, {t3=}")

        return model.eval(x + y + z)


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
hailstones = Hailstones(puzzle_input)

min_x_y = 200000000000000
max_x_y = 400000000000000
if file_name == "input_small":
    min_x_y = 7
    max_x_y = 27
print(f"Part 1: {hailstones.get_intersections(min_x_y, max_x_y)}")
print()
print(f"Part 2: {hailstones.get_coords_metric_for_line_intersecting_all_hailstones()}")
