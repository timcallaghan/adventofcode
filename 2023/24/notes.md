# Part 1

Although not stated explicitly, we assume that:

* No line has zero slope i.e. y = R (where R is real number)
* No line has infinite slope i.e. x = R (where R is a real number)

This assumption is easily verified on both small/large problem inputs.

A key aspect of solving this problem is avoiding floating point arithmatic.
For example, to test if the slopes of two lines are equal we _could_ calculate the slopes as floating point numbers and compare.
However this can lead to values that are technically equal but might differ by machine epsilon.

A better approach is to compare products as follows:

* Given line L1 with slope m1 = v1/u1 and line L2 with slope m2 = v2/u2
* Then it is sufficient to compare `v1*u2 == v2*u1`, which completely avoids floating point arithmatic

# Part 2

The hint here is the form of the line descriptions that have been supplied.
We have been given a start position and a vector describing movement per nanosecond.

This is exactly the form required to describe the line [parametrically](https://en.wikipedia.org/wiki/Line_(geometry)).

Given any point P0 (x0,y0,z0) on the line, with slope vector S(u,v,w), we can represent any other point P on the line as

`P_t(x,y,z) = P0 + tS`, where `t` is a real-valued parameter `t:(-inf, inf)`

We can easily represent all the puzzle input lines in parametric form. 
Crucially, the parameter `t` will be _the same_ for all lines since it represents integer time in nanoseconds.

The problem is asking us to find another line, in parametric form, that will eventually intersect all the supplied lines.

But, under what conditions could this be possible?

## Regulus

We have been told that:

1. None of the lines intersect in 3D space
2. Exactly one new line _will_ intersect all the lines

Lines are said to be _skew lines_ if they don't intersect and are not parallel.

Given 3 skew lines in 3D, a [regulus](https://en.wikipedia.org/wiki/Regulus_(geometry)) `R` exists that describes a [hyperboloid](https://en.wikipedia.org/wiki/Hyperboloid) of one sheet.
An opposite regulus `S` also exists in which the lines that make up `S` form [traversals](https://en.wikipedia.org/wiki/Transversal_(combinatorics)) that each intersect the lines of `R` only once.

Since we have been told that the lines are skew then they [must all belong](https://www.quora.com/Given-four-skew-lines-how-many-lines-intersect-all-of-them) to the regulus `R`.

Conversely, for an intersection to occur the intersecting line must belong to `S`.

We have the further constraint that all coordinates must be _integer_ i.e. there are no floating point numbers involved in the solution.

### How might we use this information to solve part 2 of the problem?

The constraint on integer values dictates that lines in `R` and `S` can be completely described by integer values.

Since the regulus is completely described by 3 skew lines then it is sufficient to solve for a line that intersects any three of the skew lines.

Suppose the line that satisfies the conditions is given by

```text
R(t) = R_0 + t*V_r
```

where:

* `R_0` is the initial position of the line given by `R_0 = (x, y, z)`
* `V_r` is the velocity vector of the line given by `V_r = (u, v, w)`
* `t` is the parametric parameter (must be integer >= 0)

By choosing three other hailstone lines (H1, H2, H3) and equating at times `t1, t2, t3` we produce a system of 9 simultaneous equations in 9 unknowns.

These equations are non-linear, but we are told a solution exists, so we can expect a single solution.

Once we have the equations we can use any non-linear solving mechanism to determine the 9 unknowns `x, y, z, u, v, w, t1, t2, t3`.

I initially tried using `fsolve` from `scipy.optimise` but determining an initial guess proved too difficult for the large problem input (small worked fine).
However, the `Solver` from `z3-solver` proved very capable for this task and solved it easily without the need of determining an initial guess at the solution.
