from typing import List


def get_sum_of_predictions(history_data: List[List[int]], reverse: bool = False):
    predictions: List[int] = []
    for index in range(len(history_data)):
        current_list = history_data[index][::-1] if reverse else history_data[index]

        last_vals = [current_list[-1]]

        while True:
            next_list = [x[0] - x[1] for x in zip(current_list[1:], current_list)]
            if all(value == 0 for value in next_list):
                break

            last_vals.append(next_list[-1])
            current_list = next_list

        predictions.append(sum(last_vals))

    return sum(predictions)


histories: List[List[int]] = []
file_name = "input"
with open(file_name, encoding="utf-8") as f:
    for line in f:
        histories.append([int(val) for val in line.strip().split()])

print(get_sum_of_predictions(histories))
print(get_sum_of_predictions(histories, True))
