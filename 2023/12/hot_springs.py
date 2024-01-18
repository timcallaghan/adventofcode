from typing import List, Tuple
from functools import cache
import pathlib

should_log = False


def log(message: str, depth: int):
    if should_log:
        print(" "*depth*2 + message)


# See: https://docs.python.org/3/library/functools.html
# This annotation causes function calls to be cached (i.e. memoized) and re-used rather than re-computed each time.
# Without implementing a cache the algorithm takes too long for large input.
@cache
def get_arrangements(condition_record: str, damaged_spring_groups: Tuple[int, ...], depth: int = 0) -> int:
    log(f"Checking {condition_record} against {damaged_spring_groups}", depth)

    # Check if it's not possible to satisfy the minimum spacing of damaged_spring_groups
    if len(condition_record) < sum(damaged_spring_groups) + len(damaged_spring_groups) - 1:
        log(f"{condition_record} size is too small", depth)
        return 0

    # Remove any leading/trailing "."s and solve the sub-problem
    if condition_record.startswith(".") or condition_record.endswith("."):
        sub_record = condition_record.strip(".")
        log(f"Stripped dots to yield {sub_record}", depth)
        return get_arrangements(sub_record, damaged_spring_groups, depth + 1)

    if condition_record.startswith("?"):
        # Need to split into two possible records and solve each separately
        option_1 = "." + condition_record[1:]
        option_2 = "#" + condition_record[1:]
        log(f"Splitting problem into {option_1} and {option_2}", depth)
        return get_arrangements(option_1, damaged_spring_groups, depth + 1) \
            + get_arrangements(option_2, damaged_spring_groups, depth + 1)

    # This should always be True given the problem statement, but we check anyway
    if condition_record.startswith("#"):
        # Check if we only have one group left to match
        if len(damaged_spring_groups) == 1:
            log(f"Only one group remains with size {damaged_spring_groups[0]}", depth)
            log(f"Attempting to match {condition_record}", depth)
            if len(condition_record) == damaged_spring_groups[0]:
                # If it contains any "."'s then this configuration is not possible
                if condition_record.find(".") > -1:
                    log("Failed to match because a . was found", depth)
                    return 0

                log("Exactly matched length", depth)
                return 1
            else:
                # We have a record whose length exceeds the single damaged group size
                # See if we can find a configuration that exactly matches
                # To match, it must not have any "."s inside the group at the start,
                # and it must not have any "#"'s after the group
                damaged_spring_record = condition_record[0:damaged_spring_groups[0]]
                index_of_dot = damaged_spring_record.find(".")
                if -1 < index_of_dot < damaged_spring_groups[0]:
                    # This record does not match the required configuration
                    # because there is a "." somewhere inside the record
                    log("Failed to match because a . was found", depth)
                    return 0

                remainder = condition_record[damaged_spring_groups[0]:]
                index_of_hash = remainder.find("#")
                if index_of_hash > -1:
                    log(f"Found one or more # symbols beyond the end of the final group", depth)
                    return 0

                log(f"Matched substring {damaged_spring_record} inside {condition_record}", depth)
                return 1

        # Since this must be the start of a damaged_spring_group element,
        # and that element must be followed by a ".", we can reduce the problem space
        # provided the element matches the expectation
        damaged_spring_record = condition_record[0:damaged_spring_groups[0] + 1]
        index_of_dot = damaged_spring_record.find(".")
        if -1 < index_of_dot < damaged_spring_groups[0]:
            # This record does not match the required configuration
            # because there is a "." somewhere inside the record
            log(f"Expected no dots inside {damaged_spring_record}, but found one", depth)
            return 0

        if damaged_spring_record.endswith("#"):
            log(f"Expected . or ? at end but found # - {damaged_spring_record}", depth)
            return 0

        log(f"Successfully matched {damaged_spring_record} against first group element", depth)

        # Remove the matched segment and work on the sub-problem
        sub_record = condition_record[damaged_spring_groups[0] + 1:]
        log(f"Working on sub-problem for {sub_record}", depth)

        return get_arrangements(sub_record, damaged_spring_groups[1:], depth + 1)

    raise Exception(f"Got unexpected value for {condition_record=}")


class SpringRow:
    def __init__(self, row_data: str, duplicate_factor: int):
        self.raw_data = row_data.strip()
        self.record_1, self.record_2 = self.raw_data.split(" ")
        self.damaged = [int(char) for char in self.record_2.split(",")]
        self.record_1 = "?".join([self.record_1] * duplicate_factor)
        self.damaged = self.damaged * duplicate_factor

    def __str__(self):
        return f"{self.record_1=} {self.record_2=} {self.damaged=}"


class SpringRecords:
    def __init__(self, spring_record_data: str, duplication_factor: int):
        self.all_spring_records: List[SpringRow] = []

        for line in spring_record_data.split("\n"):
            self.all_spring_records.append(SpringRow(line, duplication_factor))

    def get_total_arrangements(self) -> int:
        total_arrangements = 0
        for sr in self.all_spring_records:
            arrangements = get_arrangements(sr.record_1, tuple(sr.damaged))
            log(f"{sr.__str__()} {arrangements=}", 0)
            total_arrangements += arrangements

        return total_arrangements


all_spring_records: List[SpringRow] = []
file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()

spring_records_1 = SpringRecords(puzzle_input, 1)
print(f"Part 1: {spring_records_1.get_total_arrangements()}")

spring_records_2 = SpringRecords(puzzle_input, 5)
print(f"Part 2: {spring_records_2.get_total_arrangements()}")
