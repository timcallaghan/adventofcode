# Part 1

Basic idea is to start with one path initially and then each time we can go in more than one direction we split the path into as many duplicates as there are possible directions.

A recursive function works well for this, with the terminating conditions beings:

1. There are no more possible sections to add to the path and we are not at the end -> dead end
2. We are at the end -> complete path

Tracking path locations can be done using a set-like collection (in this case an ordered dictionary).
This allows us to do rapid detection of situations that would lead to a path containing the same location more than once.

# Part 2

Initially I tried the same algorithm on part 2 (slightly modified to ignore slopes). 
This worked fine for the small input example, however it quickly because clear that the large input would run for too long.
This is because there are now _many_ more possible paths to take (once the slope constraints are removed).

Of all these possible paths, there will be large overlap due to alternative paths converging on the same location.

For example, consider the following trail map, with start `A`, end `Z`, and each path split point labelled:

```text
#A#####################
#B..........C.........#
#.##########.########.#
#.##########.########.#
#.##########.########.#
#F..........E........D#
#.##########.########.#
#.##########.########.#
#...........G.........#
#####################Z#
```
The possible, complete paths are:

1. A -> B
   1. B -> C
      1. C -> D
         1. D -> Z (P1)
         2. D -> E
            1. E -> G -> Z (P2)
            2. E -> F -> G -> Z (P3)
      2. C -> E
         1. E -> D -> Z (P4)
         2. E -> G -> Z (P5)
         3. E -> F -> G -> Z (P6)
   2. B -> F
      1. F -> E
         1. E -> C -> D -> Z (P7)
         2. E -> D -> Z (P8)
         3. E -> G -> Z (P9)
      2. F -> G
         1. G -> E
            1. E -> C -> D -> Z (P10)
            2. E -> D -> Z (P11)
         2. G -> Z (P12)

There are 12 possible paths:

* P1 - `A -> B -> C -> D -> Z`
* P2 - `A -> B -> C -> D -> E -> G -> Z`
* P3 - `A -> B -> C -> D -> E -> F -> G -> Z`
* P4 - `A -> B -> C -> E -> D -> Z`
* P5 - `A -> B -> C -> E -> G -> Z`
* P6 - `A -> B -> C -> E -> F -> G -> Z`
* P7 - `A -> B -> F -> E -> C -> D -> Z`
* P8 - `A -> B -> F -> E -> D -> Z`
* P9 - `A -> B -> F -> E -> G -> Z`
* P10 - `A -> B -> F -> G -> E -> C -> D -> Z`
* P11 - `A -> B -> F -> G -> E -> D -> Z`
* P12 - `A -> B -> F -> G -> Z`

Within these 12 paths there is a large amount of overlap.

Specifically:

* P1 contains a segment `D -> Z` (S1) which also appears in P4, P7, P8, P10, P11
* P1 contains a segment `C -> D -> Z = C -> S1` (S2) which also appears in P7 and P10
* P2 contains a segment `G -> Z` (S3) which also appears in P3, P5, P6, P9, P12
* P2 contains a segment `E -> G -> Z = E -> S3` (S4) which also appears in P5 and P9
* P3 contains a segment `F -> G -> Z = F -> S3` (S5) which also appears in P6 and P12
* P3 contains a segment `E -> F -> G -> Z = E -> S5` (S6) which also appears in P6
* P4 contains a segment `E -> D -> Z = E -> S1` (S7) which also appears in P8 and P11
* P7 contains a segment `E -> C -> D -> Z = E -> S2` (S8) which also appears in P10

Therefore, we can represent the 12 paths as:

* P1 - `A -> B -> C -> D -> Z` = `A -> B -> S2`
* P2 - `A -> B -> C -> D -> E -> G -> Z` = `A -> B -> C -> D -> S4`
* P3 - `A -> B -> C -> D -> E -> F -> G -> Z` = `A -> B -> C -> D -> E -> S5`
* P4 - `A -> B -> C -> E -> D -> Z` = `A -> B -> C -> S7`
* P5 - `A -> B -> C -> E -> G -> Z` = `A -> B -> C -> S4`
* P6 - `A -> B -> C -> E -> F -> G -> Z` = `A -> B -> C -> S6`
* P7 - `A -> B -> F -> E -> C -> D -> Z` = `A -> B -> F -> S8`
* P8 - `A -> B -> F -> E -> D -> Z` = `A -> B -> F -> S7`
* P9 - `A -> B -> F -> E -> G -> Z` = `A -> B -> F -> S4`
* P10 - `A -> B -> F -> G -> E -> C -> D -> Z` = `A -> B -> F -> G -> S8`
* P11 - `A -> B -> F -> G -> E -> D -> Z` = `A -> B -> F -> G -> S7`
* P12 - `A -> B -> F -> G -> Z` = `A -> B -> S5`

To utilise the above, we need to be able to detect when we are stating to walk down a path segment that has already been explored.
If we detect that a segment has already been explored we can abort further processing and then resolve the path segments at the end.

## Final solution

My attempts kept running for too long due to inefficiencies in my algorithm (mostly not hitting the cache when it should have)

To solve this without burning a hole in the ozone layer I ended up [drawing on inspiration](https://github.com/jonathanpaulson/AdventOfCode/blob/master/2023/23.py) from another user.

There was a lot of overlap between my attempts at part 2, i.e. path segments for modelling vertices and edges, but the key difference is the way path splits are handled.
In the final solution approach, it's basically a depth-first search that keeps track of the largest path without storing all the path history. 
This saves on storage and computations because dead-ends are eliminated quickly and only valid paths are explored further.