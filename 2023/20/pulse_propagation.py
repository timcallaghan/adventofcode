import pathlib
from typing import Dict, List, Self, Optional, Union, Tuple
from anytree import Node, RenderTree
from math import lcm


class Pulse:
    def __init__(self, source: str, is_high: bool, destination: str):
        self.source = source
        self.is_high = is_high
        self.destination = destination


class Module:
    def __init__(self, config: str):
        self.config = config
        self.type = ""
        self.name = ""
        self.sources: List[Module] = []
        self.state: Optional[Union[bool, Dict[str, bool]]] = None
        self.has_sent_high = False

        module_data = config.strip().partition("->")
        type_name = module_data[0].strip()
        if type_name == "broadcaster" or type_name == "button":
            self.type = type_name
            self.name = type_name
        else:
            self.type = type_name[0]
            self.name = type_name[1:]

        self.destinations = [name.strip() for name in module_data[2].split(",")]

    def register_source(self, source: Self) -> None:
        self.sources.append(source)

    def init_state(self) -> None:
        self.state = None
        match self.type:
            case "%":
                self.state = False
            case "&":
                self.state = {}
                for src in self.sources:
                    self.state[src.name] = False

    def process_pulse(self, pulse: Pulse) -> List[Pulse]:
        child_pulses: List[Pulse] = []

        match self.type:
            case "broadcaster":
                self.has_sent_high = self.has_sent_high or pulse.is_high
                for d in self.destinations:
                    child_pulses.append(Pulse(self.name, pulse.is_high, d))
            case "%":
                if not pulse.is_high:
                    self.state = not self.state
                    self.has_sent_high = self.has_sent_high or self.state
                    for d in self.destinations:
                        child_pulses.append(Pulse(self.name, self.state, d))
            case "&":
                self.state[pulse.source] = pulse.is_high
                is_high = all(v for v in self.state.values())
                self.has_sent_high = self.has_sent_high or not is_high
                for d in self.destinations:
                    child_pulses.append(Pulse(self.name, not is_high, d))

        return child_pulses


class ModuleSystem:
    def __init__(self, config: str):
        self.button = Module("button -> broadcaster")
        self.modules: Dict[str, Module] = {
            self.button.name: self.button
        }

        # Create distinct modules
        for module_config in config.strip().split("\n"):
            m = Module(module_config)
            self.modules[m.name] = m

        # Wire up module sources
        for mod_key in self.modules:
            source = self.modules[mod_key]
            for destination in source.destinations:
                if destination in self.modules:
                    self.modules[destination].register_source(source)

        # Initialise starting module state
        for mod_key in self.modules:
            self.modules[mod_key].init_state()

    def press_button(self) -> Tuple[int, int]:
        low_count = 0
        high_count = 0
        current_pulses: List[Pulse] = [
            Pulse("button", False, "broadcaster")
        ]

        while len(current_pulses) > 0:
            next_pulses = []
            for p in current_pulses:
                if p.is_high:
                    high_count += 1
                else:
                    low_count += 1

                if p.destination in self.modules:
                    next_pulses.extend(self.modules[p.destination].process_pulse(p))

            current_pulses = next_pulses

        return low_count, high_count

    def __get_system_state(self) -> Dict[str, Union[bool, Dict[str, bool]]]:
        state = {}
        for m_key in self.modules:
            if m_key != "button" and m_key != "broadcaster":
                state[m_key] = self.modules[m_key].state

        return state

    def warm_up(self, number_of_presses: int) -> int:
        # State sequence is a tuple that stores:
        #   - The current system state after processing a single button press
        #   - The number of button presses to achieve the current state
        #   - The number of low pulses sent when processing the current state
        #   - The number of high pulses sent when processing the current state
        state_sequence = [
            (self.__get_system_state(), 0, 0, 0)
        ]

        state_keys = state_sequence[0][0].keys()
        cycle_start_index = 0
        cycle_end_index = number_of_presses
        has_cycle = False

        for button_press_number in range(1, number_of_presses + 1):
            low_count, high_count = self.press_button()
            current_state = self.__get_system_state()

            for previous_state in state_sequence:
                has_matching_state = True
                for s_key in state_keys:
                    has_matching_state = has_matching_state and current_state[s_key] == previous_state[0][s_key]
                    if not has_matching_state:
                        break

                if has_matching_state:
                    cycle_start_index = previous_state[1]
                    cycle_end_index = button_press_number
                    has_cycle = True
                    break

            state_sequence.append((current_state, button_press_number, low_count, high_count))
            if has_cycle:
                break

        total_low_count = 0
        total_high_count = 0

        # Button presses prior to the start of the cycle
        for ss_index in range(0, cycle_start_index):
            total_low_count += state_sequence[ss_index][2]
            total_high_count += state_sequence[ss_index][3]

        # Button presses inside the cycle
        cycle_low_count = 0
        cycle_high_count = 0
        for ss_index in range(cycle_start_index, cycle_end_index + 1):
            cycle_low_count += state_sequence[ss_index][2]
            cycle_high_count += state_sequence[ss_index][3]

        cycle_length = cycle_end_index - cycle_start_index
        q, mod = divmod(number_of_presses - cycle_start_index, cycle_length)
        cycle_low_count *= q
        cycle_high_count *= q

        total_low_count += cycle_low_count
        total_high_count += cycle_high_count

        # Button presses after the cycle
        if mod > 0:
            for button_press_number in range(number_of_presses - mod, number_of_presses + 1):
                low_count, high_count = self.press_button()
                total_low_count += low_count
                total_high_count += high_count

        return total_low_count * total_high_count

    def __is_in_node_path(self, parent_node: Node, node_name: str) -> bool:
        if parent_node.name == node_name:
            return True

        if parent_node.is_root:
            return False

        return self.__is_in_node_path(parent_node.parent, node_name)

    def __append_ancestor_nodes(self, module: Module, parent_node: Node):
        child_nodes = []
        for source in module.sources:
            if not self.__is_in_node_path(parent_node, source.name):
                child_node = Node(source.name, parent_node)
                child_nodes.append((source, child_node))
            else:
                _ = Node(f"{source.name} (cyclic)", parent_node)

        for cn in child_nodes:
            self.__append_ancestor_nodes(cn[0], cn[1])

    def trace_rx_sources(self) -> None:
        # Find module whose destination is rx
        rx_source = None
        for m_key in self.modules:
            m = self.modules[m_key]
            if "rx" in m.destinations:
                rx_source = m
                break

        root_node = Node("rx")
        rx_source_node = Node(rx_source.name, root_node)
        self.__append_ancestor_nodes(rx_source, rx_source_node)

        for pre, fill, node in RenderTree(root_node):
            print("%s%s" % (pre, node.name))

    def __append_child_nodes(self, module: Module, parent_node: Node) -> None:
        for node_name in module.destinations:
            if not self.__is_in_node_path(parent_node, node_name):
                child_node = Node(node_name, parent_node)
                if node_name in self.modules:
                    self.__append_child_nodes(self.modules[node_name], child_node)
            else:
                _ = Node(f"{node_name} (cyclic)", parent_node)

    def trace_button_children(self) -> None:
        root_node = Node(self.button.name)
        self.__append_child_nodes(self.button, root_node)

        for pre, fill, node in RenderTree(root_node):
            print("%s%s" % (pre, node.name))

    def turn_on_rx(self) -> int:
        # Find module whose destination is rx
        rx_source = None
        for m_key in self.modules:
            m = self.modules[m_key]
            if "rx" in m.destinations:
                rx_source = m
                break

        if not rx_source:
            print("Module rx was not found - aborting")
            return -1

        monitored_modules: Dict[str, Tuple[bool, int]] = {}
        for m in rx_source.sources:
            monitored_modules[m.name] = (False, 0)

        button_press_number = 1
        while True:
            self.press_button()
            has_found_all_highs = True
            for m in rx_source.sources:
                if not monitored_modules[m.name][0]:
                    monitored_modules[m.name] = (m.has_sent_high, button_press_number)
                    if monitored_modules[m.name][0]:
                        print(f"{m.name}, {button_press_number}")

                has_found_all_highs = has_found_all_highs and monitored_modules[m.name][0]

            if has_found_all_highs:
                break

            button_press_number += 1

        cycle_lengths = []
        for mm in monitored_modules.values():
            cycle_lengths.append(mm[1])

        return lcm(*cycle_lengths)


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text()
module_system = ModuleSystem(puzzle_input)

print(f"Part 1: {module_system.warm_up(1000)}")
module_system = ModuleSystem(puzzle_input)
print(f"Part 2: {module_system.turn_on_rx()}")
