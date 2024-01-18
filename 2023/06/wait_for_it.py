import pathlib
from typing import List


def get_race_win_metric(times: List[int], distances: List[int]) -> int:
    wins_for_race = []

    times_and_distances = zip(times, distances)
    for time, distance in times_and_distances:
        wins = 0
        for wait_time in range(1, time + 1, 1):
            travel_time = time - wait_time
            race_distance = wait_time * travel_time
            if race_distance > distance:
                wins += 1

        wins_for_race.append(wins)

    product = 1
    for wins in wins_for_race:
        product *= wins

    return product


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().split('\n')

times_1 = [int(time) for time in puzzle_input[0].split(':')[1].split()]
distances_1 = [int(distance) for distance in puzzle_input[1].split(':')[1].split()]
print(f"Part 1: {get_race_win_metric(times_1, distances_1)}")

times_2 = [int(puzzle_input[0].split(':')[1].replace(" ", "").strip())]
distances_2 = [int(puzzle_input[1].split(':')[1].replace(" ", "").strip())]
print(f"Part 2: {get_race_win_metric(times_2, distances_2)}")
