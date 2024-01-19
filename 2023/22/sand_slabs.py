import pathlib
from typing import List, Self, Set, Dict
import operator
import networkx as nx


class Point:
    def __init__(self, point_data: str):
        x, y, z = point_data.split(",")
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)


class Brick:
    def __init__(self, brick_id: int, brick_data: str):
        self.id = brick_id
        self.raw_data = brick_data

        start_end = brick_data.partition("~")
        p1 = Point(start_end[0])
        p2 = Point(start_end[2])

        self.min_x = p1.x if p1.x < p2.x else p2.x
        self.max_x = p1.x if p1.x > p2.x else p2.x
        self.min_y = p1.y if p1.y < p2.y else p2.y
        self.max_y = p1.y if p1.y > p2.y else p2.y
        self.min_z = p1.z if p1.z < p2.z else p2.z
        self.max_z = p1.z if p1.z > p2.z else p2.z

    def drop(self, amount: int) -> None:
        self.min_z -= amount
        self.max_z -= amount

    def intersects_xy(self, other: Self) -> bool:
        # We ignore the z direction and consider only intersection in the x-y plane i.e. bird's eye view down z axis
        return not (
            other.min_x > self.max_x
            or other.max_x < self.min_x
            or other.max_y < self.min_y
            or other.min_y > self.max_y
        )

    def is_supporting(self, other: Self) -> bool:
        return self.intersects_xy(other) and self.max_z + 1 == other.min_z


class BrickStack:
    def __init__(self, stack_data: str):
        self.all_bricks: List[Brick] = []

        brick_index = 0
        for line in stack_data.split("\n"):
            b = Brick(brick_index, line)
            self.all_bricks.append(b)
            brick_index += 1

        self.__drop_bricks()

        self.g = nx.DiGraph()
        for brick_index in range(len(self.all_bricks)):
            current_brick = self.all_bricks[brick_index]
            self.g.add_node(current_brick.id)
            for next_brick_index in range(brick_index + 1, len(self.all_bricks)):
                next_brick = self.all_bricks[next_brick_index]
                if next_brick.min_z > current_brick.max_z + 1:
                    break

                if current_brick.is_supporting(next_brick):
                    self.g.add_edge(current_brick.id, next_brick.id)

    def __drop_bricks(self) -> None:
        self.all_bricks.sort(key=operator.attrgetter('min_z'))
        for brick_index in range(0, len(self.all_bricks)):
            current_brick = self.all_bricks[brick_index]
            # Default to dropping all the way to the ground
            drop_amount = current_brick.min_z - 1
            for dropped_brick_index in range(0, brick_index):
                # Do we intersect with any dropped bricks?
                dropped_brick = self.all_bricks[dropped_brick_index]
                if current_brick.intersects_xy(dropped_brick):
                    drop_distance = current_brick.min_z - dropped_brick.max_z - 1
                    if drop_distance < drop_amount:
                        drop_amount = drop_distance

            current_brick.drop(drop_amount)

        self.all_bricks.sort(key=operator.attrgetter('min_z'))

    def get_removable_bricks_count(self) -> int:
        nodes = {}
        current_nodes = set()
        for n in list(self.g.nodes):
            nodes[n] = 0
            if self.g.in_degree[n] == 0:
                current_nodes.add(n)

        while len(current_nodes) > 0:
            next_nodes = set()
            for n in current_nodes:
                if self.g.out_degree[n] == 0:
                    nodes[n] = 1
                else:
                    has_alt_path = True
                    for d in list(self.g.successors(n)):
                        next_nodes.add(d)
                        has_alt_path = has_alt_path and self.g.in_degree[d] > 1
                    if has_alt_path:
                        nodes[n] = 1

            current_nodes = next_nodes

        return sum([nodes[n] for n in nodes])

    def __only_has_known_links(self, brick_id: int, parent_brick_id: int, dependencies: Set[int]) -> bool:
        if self.g.in_degree[brick_id] == 1:
            return True

        only_has_known_links = True
        for predecessor_id in list(self.g.predecessors(brick_id)):
            only_has_known_links = only_has_known_links \
                                   and (predecessor_id == parent_brick_id or predecessor_id in dependencies)

        return only_has_known_links

    def __determine_dependencies(self, root_brick_id: int, brick_id: int, dependencies: Dict[int, Set[int]]) -> None:
        if root_brick_id not in dependencies:
            dependencies[root_brick_id] = set()

        for successor_id in list(self.g.successors(brick_id)):
            if self.__only_has_known_links(successor_id, brick_id, dependencies[root_brick_id]):
                dependencies[root_brick_id].add(successor_id)
                self.__determine_dependencies(root_brick_id, successor_id, dependencies)

    def get_fall_total(self) -> int:
        dependencies: Dict[int, Set[int]] = {}
        fall_total = 0
        for b in self.all_bricks:
            self.__determine_dependencies(b.id, b.id, dependencies)

            fall_total += len(dependencies[b.id])

        return fall_total


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
bs = BrickStack(puzzle_input)

print(f"Part 1: {bs.get_removable_bricks_count()}")
print(f"Part 2: {bs.get_fall_total()}")
