We start by transposing the input so that we can work with rows rather than columns.

For each row, stones will naturally slide to the left until they:

1. Hit the left edge
2. Hit another stone
3. Hit a cube-shaped rock i.e. #

What is a good data structure to store this?

A queue feels appropriate as it allows us to ignore empty slots i.e. "." and just accumulate rocks until we hit a boundary condition

So let's create a class that represents a sequence of rocks and then partition each row.

For part two, it could quickly grow in computational time if we're not careful.
Calculating 1 billion spin cycles will take waaaay too long.
But, it's possible that the cycles start repeating after a while.

Consider the degenerate case where they are no cube-shaped rocks "#
Imagine we had a starting configuration like this

```text
.0.0
0.0.
```

Let's work through a cycle:

North
```text
0000
....
```

West
```text
0000
....
```

South
```text
....
0000
```

East
```text
....
0000
```

It's easy to see this has a period of 1 cycle. Therefore, after 1 billion iterations it will end up in exactly the same configuration as at the end of the first cycle.

So the key to solving this problem efficiently will be figuring out the period of the cycles.
Once we have that, we can skip forward until we are just before the 1 billionth iteration and compute the final cycles to get the end state configuration.

There is an assumption here that a period will emerge. But how can we test for it?

One easy way to do this (although not efficient in space) is to cache the function calls to compute the state after a cycle. If we ever call into the cache, that will tell us that repetition has occurred. And with a simple cycle tracking index we can easily get the period.

To figure our how many cycles we need to compute _after_ removing repetition, consider the following simplified example where we have to compute the result at the end of 10 cycles.

1. Suppose the state sequence looks like `[S1, S2, S3, S4, S5, S3, S4, S5, S3, S4]`
2. In this example, the first two states are preliminary states prior to establishing repetition
3. The period of the repetition is 3 cycles
4. To compute the state at cycle 10 we need to:
   1. Perform the preliminary cycles `[S1, S2]`
   2. Then 2x repetitions of `[S3, S4, S5]`
   3. Then the remaining steps to get to 10 cycles i.e. `[S3, S4]`


Things to note:
* The start of the first repetition is `RS = 3`
* The number of preliminary cycles is `P = RS - 1 = 2`
* The end of the first repetition is `RE = 5`
* The period of repetition is `RP = RE - RS + 1 = 3`
* Total cycles `T = 10`
* The final cycle count is `F = (T - P) % RP = (10 - 2) % 3 = 2`
