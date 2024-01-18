from typing import List, Dict
from collections import namedtuple
import pathlib
import math


Node = namedtuple('Node', 'L R')


class NetworkNavigator:
    def __init__(self, network_data: str):
        network_data_lines = network_data.split('\n\n')

        self.instructions: List[str] = [char for char in network_data_lines[0].strip()]
        self.network: Dict[str, Node] = {}

        for row in network_data_lines[1].strip().split('\n'):
            key_and_val = row.strip().split('=')
            key = key_and_val[0].strip()
            vals = key_and_val[1].replace('(', '').replace(')', '').split(',')
            node = Node(vals[0].strip(), vals[1].strip())
            self.network[key] = node

    def get_steps_to_end(self) -> int:
        current_index = 0
        steps = 0
        current_key = "AAA"
        if current_key not in self.network:
            print(f"Start locations not valid")
            return -1

        while True:
            node = self.network[current_key]
            direction = self.instructions[current_index]
            current_key = getattr(node, direction)
            steps += 1
            current_index += 1
            if current_index == len(self.instructions):
                current_index = 0

            if current_key == "ZZZ":
                break

        return steps

    def get_steps_to_all_ends(self) -> int:
        # Let's test to see if Lowest Common Multiple (LCM) might work
        # For this to hold true, each __A node must reach exactly one distinct __Z node.
        # Additionally, once the __Z node is reached further iteration should re-reach the same __Z node in
        # exactly the same amount of steps that it took to initially reach the __Z node from the __A node.
        starting_nodes = [key for key in self.network if key.endswith("A")]
        current_nodes = starting_nodes.copy()
        ending_nodes = starting_nodes.copy()
        steps_to_reach_Z = [0 for _ in range(len(starting_nodes))]
        current_index = 0
        while True:
            nodes = [self.network[key] for key in current_nodes]
            direction = self.instructions[current_index]
            current_nodes = [getattr(node, direction) for node in nodes]

            for index in range(len(steps_to_reach_Z)):
                if not ending_nodes[index].endswith("Z"):
                    steps_to_reach_Z[index] += 1

                if current_nodes[index].endswith("Z"):
                    ending_nodes[index] = current_nodes[index]

            current_index += 1
            if current_index == len(self.instructions):
                current_index = 0

            nodes_ending_in_Z = [node for node in ending_nodes if node.endswith("Z")]
            if len(nodes_ending_in_Z) == len(current_nodes):
                break

        return math.lcm(*steps_to_reach_Z)


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()

network_navigator = NetworkNavigator(puzzle_input)
print(f"Part 1: {network_navigator.get_steps_to_end()}")
print(f"Part 2: {network_navigator.get_steps_to_all_ends()}")
