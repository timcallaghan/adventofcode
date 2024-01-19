This feels like another dynamic programming problem because there are a large number of permutations that need to be evaluated.

The constraints on the problem space for a grid of size MxN are:

1. We _must_ start at (0,0)
2. We _must_ end at (M-1,N-1)
3. The initial cost of (0, 0) is zero, but subsequent visits result in a cost
4. We can't leave the city i.e. certain moves are excluded at the boundary
5. The next move _must_ be one of at most three choices:
   1. L -> Turn left and advance one space
   2. R -> Turn right and advance one space
   3. A -> Continue forwards one space, but _only_ if we have not done so for the 3 previous moves

To minimise something it is helpful to have an initial starting solution that can be used as a baseline comparison.

Since heat loss values at each grid point are _positive_ (in range `[1,9]`) the cost must always _increase_ when moving to the next grid cell.

We assume this problem has a global minimum, which needs to be unique to a single path.

If at any stage the cost of an incomplete path exceeds the current best minimum we can immediately exclude it.

Visual analysis of the puzzle input shows that higher heat loss numbers are more likely to reside towards the centre of the city, whereas lower heat loss numbers are more likely to reside around the edge of the city.
However, it's not clear how we might exploit this?

Avoiding cycles will be an important optimisation. For example, a path that only turns left will loop indefinitely until it exceeds the current minimum cost. However, this will consume needless CPU cycles so avoiding this situation is highly desirable.
More generally, larger cycles also exist e.g. L, A, L, A, L, A

Paths that contain alternating pairs of (L, R) are more likely to reach the end before exceeding the current minimum.

Paths that head back on themselves will be non-optimal because it should always be possible to remove the loop in the path.

Consider the solution to the small example
```text
2>>34^>>>1323
32v>>>35v5623
32552456v>>54
3446585845v52
4546657867v>6
14385987984v4
44578769877v6
36378779796v>
465496798688v
456467998645v
12246868655<v
25465488877v5
43226746555v>
```

The path is: `A, A, R, L, A, A, L, R, A, A, R, A, L, A, R, A, L, R, A, A, L, R, A, A, R, L, A, L`

In this optimal path, we never exceed more than 2 `L` or 2 `R` before deflecting in the opposite direction.



## Timings

Timing my solution for different subsets of the `input_small` file.

| Size | Time   |
|------|--------|
| 8    | 0.5s   |
| 9    | 4.3s   |
| 10   | 18.9s  |
| 11   | 78.4s  |
| 12   | 120.9s |
| 13   | 149.3s |

I _think_ I can explain this by:

1. Small problem sizes are trivial and quick to evaluate all possible paths
2. As sizes get larger the number of paths increases, which increases run time
3. For large sizes, we can short-circuit out of paths more quickly because the taxicab distance allows us to detect non-optimal solutions faster

Running this algorithm on the `input` file took a long time!
I eventually terminated it (after a couple of hours) with current global minimum of `1305` but it was unclear how much remained to be explored. I tested this solution but it was too large.

## Alternative algorithms

### Preferential minimum

Another way to minimise the cost is to preferentially choose the smallest increment out of the available directions, and explore that path first.

This is an alternative to the strategy of "ahead, then left, then right".

One reason this is not such a good idea can be seen by examining the `input_small` file.
If we apply this algorithm we see that the solution given in the problem description won't be encountered until after _all paths heading south_ have been exhausted.

### Dijkstra's algorithm

We can represent the city as a graph of vertices and edges.

For example, consider the following city layout
```text
241
321
325
```

We can reformulate this so that the numbers in the grid represent the weights attached to the edges between two vertices.

```text
V00-4-V01-1-V02
 |     |     |
 3     2     1
 |     |     | 
V10-2-V11-1-V12
 |     |     |
 3     2     5
 |     |     | 
V20-2-V21-5-V22
```

There is an assumption that we never want to return to `V00` as part of a minimum solution - seems valid as it would imply a shorter path that just avoids the loop-back to `V00`.

Additionally, minimum solutions are likely only possible if we assume this is a _directed graph_ i.e. once we have traversed from V(n-1) to V(n) we assume we will never go from V(n) to V(n-1) in the current path.

Once the problem is represented as a directed, weighted graph we can use [Dijkstra's](https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/) to solve for the global minimum. [Another](https://courses.lumenlearning.com/waymakermath4libarts/chapter/shortest-path/) explanation of Dijkstra's algorithm.

After contemplating this further, this problem is not a good fit for Dijkstra's because the edges between available vertices are not constant throughout the solution process 
i.e. depending on if we've advanced 3 spaces forward the next vertex in the forward direction might not always be connected in the graph.
Therefore Dijkstra's algorithm is not applicable sadly.

## Final solution

I ended up drawing inspiration from [another user's solution](https://github.com/jonathanpaulson/AdventOfCode/blob/master/2023/17.py). 
I should have followed my initial gut instinct and leant into a DP solution! 

The basic idea is:

1. Start at the start
2. Explore the map according to the puzzle rules
   1. Importantly, we keep track of where we came from using immutable tuples and a cache
3. If at any point we re-enter a block under exactly the same conditions then we short-circuit out of the search quickly
4. We use a minimum priority queue with the cost as the priority value so that we preferentially explore the lowest cost paths first 
   1. This is technically not needed since we'll explore all paths no matter the processing order
