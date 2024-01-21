# Part 1

This is a [graph partitioning](https://en.wikipedia.org/wiki/Graph_partition) problem.

Specifically, it involves finding a minimum edge cut set S that will partition the graph into two sub-graphs.
Importantly, for this specific problem the size of S must be 3.

Networkx has this functionality built into its [minimum_edge_cut](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.connectivity.cuts.minimum_edge_cut.html#minimum-edge-cut) routine.

Provided the set size of the minimum edge cut equals 3 then the answer can be computed by:

1. Finding the minimum edge cut set S
2. Removing the edges in S from the the graph
3. Computing the subgraph sizes for the two disconnected graphs and multiplying them together
