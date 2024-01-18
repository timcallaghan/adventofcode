def extract_game_number(text: str):
    return int(text[5:])


class BagConstraints:
    def __init__(self, max_red: int, max_green: int, max_blue: int):
        self.values = {"red": max_red, "green": max_green, "blue": max_blue}


class Cube:
    def __init__(self, cube_data: str):
        number_and_colour = cube_data.partition(" ")
        self.number = int(number_and_colour[0])
        self.colour = number_and_colour[2]

    def __str__(self):
        return f"{self.number} {self.colour}"


class Turn:
    def __init__(self, turn_data: str):
        self.cubes = []
        for cube_data in turn_data.split(","):
            self.cubes.append(Cube(cube_data.strip()))

    def satisfies_constraints(self, constraints: BagConstraints) -> bool:
        for cube in self.cubes:
            if cube.number > constraints.values[cube.colour]:
                return False
        return True


class Game:
    def __init__(self, game_data: str):
        game_and_data = game_data.partition(":")
        self.game_number = extract_game_number(game_and_data[0])
        self.turns = []
        for turn_data in game_and_data[2].split(";"):
            self.turns.append(Turn(turn_data.strip()))

        self.minimum_cube_counts = {"red": 0, "green": 0, "blue": 0}
        for turn in self.turns:
            for cube in turn.cubes:
                if cube.number > self.minimum_cube_counts[cube.colour]:
                    self.minimum_cube_counts[cube.colour] = cube.number

    def satisfies_constraints(self, constraints: BagConstraints) -> bool:
        for turn in self.turns:
            if not turn.satisfies_constraints(constraints):
                return False
        return True

    def power(self):
        return self.minimum_cube_counts["red"] \
            * self.minimum_cube_counts["green"] \
            * self.minimum_cube_counts["blue"]


def print_game_data(data):
    for g in data:
        print(g.game_number)
        for turn in g.turns:
            print([cube.__str__() for cube in turn.cubes])


all_game_data = []

file_name = "input_small"
with open(file_name, encoding="utf-8") as f:
    for line in f:
        all_game_data.append(Game(line))

# print_game_data(all_game_data)

bag_constraints = BagConstraints(12, 13, 14)

valid_games = []
for game in all_game_data:
    if game.satisfies_constraints(bag_constraints):
        valid_games.append(game)

# print_game_data(valid_games)

print(f"Part 1: {sum(game.game_number for game in valid_games)}")
print(f"Part 2: {sum(game.power() for game in all_game_data)}")
