def replace_word_with_digit(row: str) -> str:
    return row.replace("one", "1") \
        .replace("two", "2") \
        .replace("three", "3") \
        .replace("four", "4") \
        .replace("five", "5") \
        .replace("six", "6") \
        .replace("seven", "7") \
        .replace("eight", "8") \
        .replace("nine", "9")


def extract_first_digit(row: str, include_words: bool) -> int:
    for i in range(len(row)):
        if row[i].isdigit():
            return int(row[i])

        if include_words:
            replaced = replace_word_with_digit(row[0:i + 1])
            if replaced[-1].isdigit():
                return int(replaced[-1])

    return 0


def extract_last_digit(row: str, include_words: bool) -> int:
    length = len(row)
    for i in range(length - 1, -1, -1):
        if row[i].isdigit():
            return int(row[i])

        if include_words:
            replaced = replace_word_with_digit(row[i:length])
            if replaced[0].isdigit():
                return int(replaced[0])

    return 0


def extract_calibration(row: str, include_words=False) -> int:
    first = extract_first_digit(row, include_words)
    last = extract_last_digit(row, include_words)

    calibration = first * 10 + last
    return calibration


should_log = False
part_1_digits = []
part_2_digits = []

file_name = "input_small"
with open(file_name, encoding="utf-8") as f:
    for line in f:
        digit_1 = extract_calibration(line)
        part_1_digits.append(digit_1)

        digit_2 = extract_calibration(line, True)
        part_2_digits.append(digit_2)

        if should_log and digit_1 != digit_2:
            print(f"{line.strip()} {digit_1} {digit_2}")

print(f"Part 1: {sum(part_1_digits)}")
print(f"Part 2: {sum(part_2_digits)}")
