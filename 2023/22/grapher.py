import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt

G = nx.DiGraph()
G.add_edge("A", "B")
G.add_edge("A", "C")
G.add_edge("B", "D")
G.add_edge("B", "E")
G.add_edge("C", "D")
G.add_edge("C", "E")
G.add_edge("D", "F")
G.add_edge("E", "F")
G.add_edge("F", "G")

for s in G.successors("A"):
    print(s)

print(list(G.edges))
print(list(G.nodes))

print(G.degree)
print(G.in_degree)
print(G.out_degree)

print(nx.is_directed_acyclic_graph(G))

nodes = {}
for n in list(G.nodes):
    nodes[n] = 0

current_nodes = set()
current_nodes.add("A")

while len(current_nodes) > 0:
    next_nodes = set()
    for n in current_nodes:
        if G.out_degree[n] == 0:
            nodes[n] = 1
        else:
            has_alt_path = True
            for d in list(G.successors(n)):
                next_nodes.add(d)
                has_alt_path = has_alt_path and G.in_degree[d] > 1
            if has_alt_path:
                nodes[n] = 1

    current_nodes = next_nodes

for n in nodes:
    print(f"{n}, {nodes[n]}")

# pos = nx.spring_layout(G)
# nx.draw(G, pos, with_labels=True, font_weight='bold')
# plt.savefig("test.png")

