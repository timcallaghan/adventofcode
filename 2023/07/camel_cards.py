import pathlib
from typing import List, Dict
import operator


# To make sorting trivial we transform the existing card values to a range that is monotonically decreasing
# A -> z
# K -> y
# Q -> w
# J -> v, or l (use_jokers == True)
# T -> u
# 9 -> t
# 8 -> s
# 7 -> r
# 6 -> q
# 5 -> p
# 4 -> o
# 3 -> n
# 2 -> m
def normalise_hand_string(hand_string: str, use_jokers: bool) -> str:
    return hand_string.replace("A", "z") \
        .replace("K", "y") \
        .replace("Q", "w") \
        .replace("J", "l" if use_jokers else "v") \
        .replace("T", "u") \
        .replace("9", "t") \
        .replace("8", "s") \
        .replace("7", "r") \
        .replace("6", "q") \
        .replace("5", "p") \
        .replace("4", "o") \
        .replace("3", "n") \
        .replace("2", "m")


# Using conventions as follows
# 7: Five of a kind, where all five cards have the same label: AAAAA
# 6: Four of a kind, where four cards have the same label and one card has a different label: AA8AA
# 5: Full house, where three cards have the same label, and the remaining two cards share a different label: 23332
# 4: Three of a kind, where three cards have the same label, and the remaining two cards are each different from any
#    other card in the hand: TTT98
# 3: Two pair, where two cards share one label, two other cards share a second label, and the remaining card has a
#     third label: 23432
# 2: One pair, where two cards share one label, and the other three cards have a different label from the pair and
#    each other: A23A4
# 1: High card, where all cards' labels are distinct: 23456
def get_hand_kind(hand_string: str, use_jokers: bool) -> int:
    card_counts: Dict[str, int] = {}
    joker_count = 0
    for char in hand_string:
        if use_jokers and char == "J":
            joker_count += 1
        elif char not in card_counts:
            card_counts[char] = 1
        else:
            card_counts[char] += 1

    if use_jokers:
        # Increase the card with the highest count by joker_count
        if joker_count == 5:
            card_counts["J"] = 5
        elif joker_count > 0:
            highest_count_card = max(card_counts, key=card_counts.get)
            card_counts[highest_count_card] += joker_count

    match len(card_counts.keys()):
        case 1:
            return 7
        case 2:
            for key in card_counts:
                if card_counts[key] > 3:
                    return 6
            return 5
        case 3:
            for key in card_counts:
                if card_counts[key] > 2:
                    return 4
            return 3
        case 4:
            return 2
        case 5:
            return 1


class HandBid:
    def __init__(self, data: str, use_jokers: bool):
        hand_and_bid = data.strip().split()
        self.hand_str = hand_and_bid[0]
        self.bid = int(hand_and_bid[1])
        self.normalised_hand = normalise_hand_string(self.hand_str, use_jokers)
        self.hand_kind = get_hand_kind(self.hand_str, use_jokers)


class Hands:
    def __init__(self, hands_data: str, use_jokers: bool):
        self.all_hands: List[HandBid] = []
        for line in hands_data.strip().split("\n"):
            self.all_hands.append(HandBid(line, use_jokers))

    def get_total_winnings(self) -> int:
        self.all_hands.sort(key=operator.attrgetter('hand_kind', 'normalised_hand'))
        total_winnings = 0
        for rank in range(1, len(self.all_hands) + 1):
            total_winnings += rank * self.all_hands[rank - 1].bid

        return total_winnings


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()

hands_1 = Hands(puzzle_input, False)
print(f"Part 1: {hands_1.get_total_winnings()}")

hands_2 = Hands(puzzle_input, True)
print(f"Part 2: {hands_2.get_total_winnings()}")
