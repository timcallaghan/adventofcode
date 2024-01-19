import pathlib
from typing import Dict, List, Self, Tuple
import copy
import itertools


class Part:
    def __init__(self, part_data: str, x: int = 0, m: int = 0, a: int = 0, s: int = 0):
        self.x = x
        self.m = m
        self.a = a
        self.s = s

        if len(part_data) > 0:
            part_data = part_data.replace("{", "").replace("}", "")
            char_vals = part_data.split(",")
            for char_val in char_vals:
                char, val = char_val.split("=")
                match char:
                    case "x":
                        self.x = int(val)
                    case "m":
                        self.m = int(val)
                    case "a":
                        self.a = int(val)
                    case "s":
                        self.s = int(val)

    def total(self) -> int:
        return self.x + self.m + self.a + self.s

    def get_val(self, char: str) -> int:
        match char:
            case "x":
                return self.x
            case "m":
                return self.m
            case "a":
                return self.a
            case "s":
                return self.s


class SpacePartition:
    def __init__(self, max_size: int, entry: str):
        self.entry = entry
        self.min_x = 1
        self.max_x = max_size
        self.min_m = 1
        self.max_m = max_size
        self.min_a = 1
        self.max_a = max_size
        self.min_s = 1
        self.max_s = max_size

    def visualise(self):
        print(
            f"{self.entry}, "
            f"x ({self.min_x: <4},{self.max_x: <4}), "
            f"m ({self.min_m: <4},{self.max_m: <4}), "
            f"a ({self.min_a: <4},{self.max_a: <4}), "
            f"s ({self.min_s: <4},{self.max_s: <4}), "
            f"vol = {self.volume()}"
        )

    def volume(self) -> int:
        x = self.max_x - self.min_x + 1
        m = self.max_m - self.min_m + 1
        a = self.max_a - self.min_a + 1
        s = self.max_s - self.min_s + 1
        return x*m*a*s

    def split(self, dimension: str, idx: int) -> Tuple[Self, Self]:
        left = copy.copy(self)
        right = copy.copy(self)

        match dimension:
            case "x":
                left.max_x = idx
                right.min_x = idx + 1
            case "m":
                left.max_m = idx
                right.min_m = idx + 1
            case "a":
                left.max_a = idx
                right.min_a = idx + 1
            case "s":
                left.max_s = idx
                right.min_s = idx + 1

        return left, right


class Workflow:
    def __init__(self, workflow_data: str):
        key, steps = workflow_data.strip().split("{")
        self.key = key
        self.step_data = steps.strip("}")
        self.steps: List[str] = []
        for s in self.step_data.split(","):
            self.steps.append(s)

    def evaluate(self, p: Part) -> str:
        for s in self.steps:
            if s.find(":") == -1:
                return s

            comparison, result = s.split(":")
            if comparison.find("<") > -1:
                prop, val = comparison.split("<")
                if p.get_val(prop) < int(val):
                    return result
            else:
                prop, val = comparison.split(">")
                if p.get_val(prop) > int(val):
                    return result


def decompose_step(step: str) -> Tuple[str, str, str, int]:
    if step.find(":") == -1:
        return step, "", "", -1

    comparison, result = step.split(":")
    if comparison.find("<") > -1:
        prop, val = comparison.split("<")
        return result, prop, "<", int(val) - 1
    else:
        prop, val = comparison.split(">")
        return result, prop, ">", int(val)


class WorkflowEvaluator:
    def __init__(self, workflows_data: str):
        self.space_partitions: List[SpacePartition] = []
        self.all_workflows: Dict[str, Workflow] = {}
        for w in workflows_data.split():
            workflow = Workflow(w)
            self.all_workflows[workflow.key] = workflow

    def is_accepted(self, p: Part) -> bool:
        current_key = "in"
        while True:
            result = self.all_workflows[current_key].evaluate(p)
            if result == "A":
                return True
            elif result == "R":
                return False
            else:
                current_key = result

    def get_total_accepted(self, max_size: int) -> int:
        start = SpacePartition(max_size, "in")
        stack = [start]

        while len(stack) > 0:
            sp = stack.pop()
            if sp.entry == "A" or sp.entry == "R":
                self.space_partitions.append(sp)
                continue

            w = self.all_workflows[sp.entry]
            w_sp_stack = []
            for c1, c2 in itertools.pairwise(w.steps):
                target, dim, op, idx = decompose_step(c1)
                sp1, sp2 = sp.split(dim, idx)
                if op == "<":
                    left = sp1
                    right = sp2
                else:
                    left = sp2
                    right = sp1

                left.entry = target
                w_sp_stack.append(left)

                target, dim, op, idx = decompose_step(c2)
                if idx == -1:
                    right.entry = target
                    w_sp_stack.append(right)
                else:
                    sp = right

            while len(w_sp_stack) > 0:
                stack.append(w_sp_stack.pop())

        total_accepted = max_size**4
        for space_partition in workflow_evaluator.space_partitions:
            # space_partition.visualise()
            if space_partition.entry == "R":
                total_accepted -= space_partition.volume()
        return total_accepted


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text()
workflows, parts = puzzle_input.split("\n\n")

workflow_evaluator = WorkflowEvaluator(workflows)

all_parts: List[Part] = []
total = 0
for part_line in parts.split():
    part = Part(part_line.strip())
    all_parts.append(part)
    if workflow_evaluator.is_accepted(part):
        total += part.total()

print(f"Part 1: {total}")
print(f"Part 2: {workflow_evaluator.get_total_accepted(4000)}")
