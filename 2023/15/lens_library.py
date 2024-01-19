import pathlib
from collections import OrderedDict
from typing import List


def get_hash(str_val: str) -> int:
    current_val = 0
    for char in str_val:
        ascii_val = ord(char)
        current_val += ascii_val
        current_val *= 17
        current_val = current_val % 256

    return current_val


class Box:
    def __init__(self, box_id: int):
        self.box_id = box_id
        self.lens_slots = OrderedDict()

    def remove_lens(self, lens_label: str) -> None:
        if lens_label in self.lens_slots:
            self.lens_slots.pop(lens_label)

    def add_lens(self, lens_label: str, lens_id: int):
        if lens_label in self.lens_slots:
            self.lens_slots[lens_label] = lens_id
        else:
            self.lens_slots[lens_label] = lens_id

    def get_focussing_power(self) -> int:
        total = 0
        box_number_offset = self.box_id + 1
        for idx, key in enumerate(self.lens_slots):
            slot_index = idx + 1
            focal_length = self.lens_slots[key]

            total += box_number_offset * slot_index * focal_length

        return total


file_name = "input_small"
instructions = pathlib.Path(file_name).read_text().strip().split(",")

boxes: List[Box] = []
for box_number in range(256):
    boxes.append(Box(box_number))

part_1_total = 0
for init_sequence in instructions:
    part_1_total += get_hash(init_sequence)

    if init_sequence.find("=") > -1:
        l_label, l_id = init_sequence.split("=")
        box_id_from_hash = get_hash(l_label)
        boxes[box_id_from_hash].add_lens(l_label, int(l_id))
    else:
        l_label = init_sequence[:-1]
        box_id_from_hash = get_hash(l_label)
        boxes[box_id_from_hash].remove_lens(l_label)


print(f"Part 1 answer: {part_1_total}")

total_focussing_power = 0
for index in range(256):
    if len(boxes[index].lens_slots) != 0:
        # print(f"Box {index}: {boxes[index].lens_slots}")
        total_focussing_power += boxes[index].get_focussing_power()

print(f"Part 2 answer: {total_focussing_power}")
