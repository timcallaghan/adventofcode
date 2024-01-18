from typing import List, Dict


class Card:
    def __init__(self, data: str):
        card_and_data = data.partition(":")
        self.card_number = card_and_data[0].strip()

        game_data = card_and_data[2].strip().partition("|")
        self.winning_numbers = {int(num) for num in game_data[0].strip().split()}
        self.numbers = {int(num) for num in game_data[2].strip().split()}

    def card_points(self) -> int:
        total_matches = self.total_matches()
        if total_matches > 0:
            return 2**(total_matches-1)
        return 0

    def total_matches(self) -> int:
        return len(self.numbers.intersection(self.winning_numbers))

    def __str__(self):
        return f"{self.card_number} {self.winning_numbers} {self.numbers} {self.total_matches()} {self.card_points()}"


all_cards: List[Card] = []

file_name = "input_small"
with open(file_name, encoding="utf-8") as f:
    for line in f:
        all_cards.append(Card(line))

for card in all_cards:
    print(card.__str__())

print(f"Part 1: {sum(c.card_points() for c in all_cards)}")

card_counts: Dict[int, int] = {}
for index in range(len(all_cards)):
    card_number = index + 1
    if card_number not in card_counts:
        card_counts[card_number] = 1
    else:
        card_counts[card_number] += 1

    total_card_copies = card_counts[card_number]

    for match_index in range(all_cards[index].total_matches()):
        winning_card_number = card_number + match_index + 1
        if winning_card_number not in card_counts:
            card_counts[winning_card_number] = total_card_copies
        else:
            card_counts[winning_card_number] += total_card_copies

print(f"Part 2: {sum(card_counts.values())}")
