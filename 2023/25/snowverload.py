import pathlib
import networkx as nx
import matplotlib.pyplot as plt


class GraphAnalyser:
    def __init__(self, graph_data: str):
        self.g = nx.Graph()
        for line in graph_data.split("\n"):
            node, _, connections = line.strip().partition(":")
            for other_node in connections.strip().split(" "):
                self.g.add_edge(node, other_node)

    def visualise(self, filename: str) -> None:
        pos = nx.spring_layout(self.g)
        nx.draw(self.g, pos, with_labels=True, font_weight='bold')
        plt.savefig(f"{filename}.png")
        plt.clf()

    def partition_graph(self, cut_size: int) -> int:
        s = nx.minimum_edge_cut(self.g)
        if len(s) != cut_size:
            print(f"Minimum edge cut of size {len(s)} is not the same as expected cut size {cut_size}")
            return -1
        else:
            print(f"Found cut set of size {cut_size}: {s}")

        for e in s:
            self.g.remove_edge(e[0], e[1])

        print("Edges removed")
        result = 1
        for c in nx.connected_components(self.g):
            result *= len(nx.nodes(self.g.subgraph(c)))

        return result


file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().strip()
ga = GraphAnalyser(puzzle_input)

# ga.visualise(file_name)
print(f"Part 1: {ga.partition_graph(3)}")
# ga.visualise(f"{file_name}_after_cut")
