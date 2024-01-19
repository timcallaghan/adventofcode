# Part 1

We solve this as follows:

1. Using the dig plan we incrementally build up the perimeter, where it's possible for coordinates to become negative
   1. At the same time, we determine if the current section of perimeter represents a vertical segment
2. Translate all perimeter coordinates to a 0-based top-left origin
3. Sort the perimeter pieces by row and col
4. Build up a matrix of chars that represents the entire dig plan
5. Iterate over all possible locations in the map and determine if it's inside the perimeter
   1. This uses an edge-crossing count algorithm (even is out, odd is in)

# Part 2

The algorithm used for part 1 will not work efficiently for part 2, mainly due to the very large number of point testing needed to determine if a point is inside the area.

Therefore, there must be an easier way to compute this for large maps!

Drawing inspiration from [another user's answer](https://github.com/jonathanpaulson/AdventOfCode/blob/master/2023/18.py) we can use [Pick's Theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem).

## Pick's Theorem

Suppose that a polygon has integer coordinates for all of its vertices. 
Let `i` be the number of integer points interior to the polygon, and let `b` be the number of integer points on its boundary (including both vertices and points along the sides). 
Then the area `A` of this polygon is:

```text
A = i + b/2 − 1
```

Pick's theorem is applicable here because the perimeter points all lie on integer coordinates.
Importantly, the coordinates of each vertex are at the _centre_ of each dug-out 1x1 cube.

Rearranging, we have

```text
i = A - b/2 + 1
```

and since the answer is given by `i+b` we have

```text
i+b = A + b/2 + 1
```

where `A` is the area _internal_ to the polygon described by our vertices.

Essentially this is saying the total area of the lagoon is "the area internal to the polygon described by vertices plus the outer area outside the polygon path described by the perimeter that will ensure the 1x1x1 cube condition is met".

We still need to compute the area of the interior of the shape.
We can do so using [Green's Theorem, or the Shoelace Algorithm](https://ximera.osu.edu/mooculus/calculus3/greensTheorem/digInGreensTheoremAsAPlanimeter).

## Shoelace Algorithm

The [Shoelace Algorithm](https://en.wikipedia.org/wiki/Shoelace_formula) can be used to efficiently calculate the area of any polygon `P`.

Let the `n` vertices of P be given by `P_i = (x_i, y_i)` where `i=1,2,3,...,n`.

The area `A` of the polygon `P` is given by 

```text
             ( | x_1 x_2 x_3 ... x_n x_1 | )
A = 1/2 * abs( |                         | )
             ( | y_1 y_2 y_3 ... y_n y_1 | )
```

where `|...|` is the standard [determinant](https://en.wikipedia.org/wiki/Determinant) definition. 
