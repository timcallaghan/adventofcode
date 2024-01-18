import pathlib
from typing import Tuple
from enum import Enum


class SymmetryDirection(Enum):
    vertical = 0,
    horizontal = 1


def transpose_pattern(pattern_data: str) -> str:
    rows = pattern_data.split()
    transposed = []
    for col in range(len(rows[0])):
        transposed.append("")

    for row in rows:
        for index, char in enumerate(row.strip()):
            transposed[index] += char

    return "\n".join(transposed)


def check_pattern_difference(p1: str, p2: str) -> bool:
    if p1 == p2:
        return False

    differences = 0
    for i in range(len(p1)):
        if p1[i] != p2[i]:
            differences += 1

    return differences == 1


def get_symmetry_direction(pattern_data: str, correct_smudge: bool) -> Tuple[int, SymmetryDirection]:
    rows = pattern_data.split()
    for pivot_index in range(1, len(rows)):
        left = rows[pivot_index - 1]
        right = rows[pivot_index]

        is_off_by_one = correct_smudge and check_pattern_difference(left, right)

        if left == right or is_off_by_one:
            is_symmetric_to_start = True
            for check_index in range(1, pivot_index):
                left_index = pivot_index - 1 - check_index
                right_index = pivot_index + check_index
                if left_index < 0 or right_index >= len(rows):
                    # Pattern repeats up to L or R boundary, which is a valid reflection
                    break

                check_left = rows[pivot_index - 1 - check_index]
                check_right = rows[pivot_index + check_index]
                if check_left != check_right:
                    if correct_smudge and not is_off_by_one:
                        is_off_by_one = check_pattern_difference(check_left, check_right)
                        if not is_off_by_one:
                            is_symmetric_to_start = False
                            break
                    else:
                        is_symmetric_to_start = False
                        break

            if is_symmetric_to_start and (not correct_smudge or is_off_by_one):
                return pivot_index, SymmetryDirection.horizontal

    return -1, SymmetryDirection.vertical


def get_count_and_direction(pattern_data: str, correct_smudge: bool) -> Tuple[int, SymmetryDirection]:
    rows, sym_dir = get_symmetry_direction(pattern_data, correct_smudge)
    if sym_dir == SymmetryDirection.horizontal:
        return rows, sym_dir
    else:
        transposed = transpose_pattern(pattern_data)
        cols, _ = get_count_and_direction(transposed, correct_smudge)
        return cols, SymmetryDirection.vertical


def get_pattern_summary_metric(pattern_data: str, correct_smudge: bool) -> int:
    total_cols = 0
    total_rows = 0
    for pattern in pattern_data.split("\n\n"):
        cnt, direction = get_count_and_direction(pattern, correct_smudge)
        if direction == SymmetryDirection.vertical:
            total_cols += cnt
        else:
            total_rows += cnt

    return 100 * total_rows + total_cols


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
print(f"Part 1: {get_pattern_summary_metric(puzzle_input, False)}")
print(f"Part 2: {get_pattern_summary_metric(puzzle_input, True)}")
