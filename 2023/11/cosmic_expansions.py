from typing import List


class Galaxy:
    def __init__(self, x: int, y: int):
        self.x_contracted = x
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"


class GalaxyMap:
    def __init__(self, file: str, expansion_factor: int):
        self.raw_data: List[List[str]] = []
        self.galaxies: List[Galaxy] = []
        self.expansion_factor = expansion_factor

        with open(file, encoding="utf-8") as f:
            y = 0
            for line in f:
                row_data = []
                has_galaxies = False
                for index, char in enumerate(line.strip()):
                    row_data.append(char)
                    if char == "#":
                        has_galaxies = True
                        self.galaxies.append(Galaxy(index, y))

                self.raw_data.append(row_data)
                # Expand in the vertical direction now as it's easy to do
                if has_galaxies:
                    y += 1
                else:
                    y += self.expansion_factor

        # Expand in the horizontal direction
        for col in range(len(self.raw_data[0])):
            has_galaxies = False
            for row in range(len(self.raw_data)):
                if self.raw_data[row][col] == "#":
                    has_galaxies = True
                    break

            if not has_galaxies:
                for galaxy in self.galaxies:
                    if galaxy.x_contracted > col:
                        galaxy.x += self.expansion_factor - 1

    def get_shortest_paths(self) -> List[int]:
        shortest_paths: List[int] = []
        for g1_index in range(len(self.galaxies) - 1):
            for g2_index in range(g1_index + 1, len(self.galaxies)):
                g1 = self.galaxies[g1_index]
                g2 = self.galaxies[g2_index]
                distance = abs(g2.x - g1.x) + abs(g2.y - g1.y)
                shortest_paths.append(distance)

        return shortest_paths

    def display(self):
        for row in self.raw_data:
            print(row)


file_name = "input_small"

galaxy_map = GalaxyMap(file_name, 2)
distances = galaxy_map.get_shortest_paths()
print(f"Part 1: {sum(distances)}")

galaxy_map = GalaxyMap(file_name, 1000000)
distances = galaxy_map.get_shortest_paths()
print(f"Part 2: {sum(distances)}")
