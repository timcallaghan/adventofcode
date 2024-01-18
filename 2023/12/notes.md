This one had me scratching my head for quite some time!

Full disclosure, I needed "hints" to solve this - initially I couldn't even think of how I would go about this!

It's highlighted a few things for me:

1. Day-to-day enterprise programming _rarely_ requires you to use recursive programming techniques
   1. I suspect this is mostly due to enterprise programming being forms-over-data for the most part which rarely requires recursion
   2. This is a pity because recursive programming can make light work of certain problems
2. Because enterprise programmers rarely use recursive programming, reasoning through recursive logic is _difficult_ for the untrained programmer
3. [Dynamic Programming (DP)](https://en.wikipedia.org/wiki/Dynamic_programming) is fascinating!
   1. Recursion by itself it _not_ DP, however DP often utilises recursion as part of divide-and-conquer algorithms
   2. Memoization is highly effective at speeding up DP programs that involve a lot of overlapping sub-problems
4. Python was incredibly efficient at solving this problem
   1. Syntax for handling sub-problems (i.e. array slicing of arguments) is a breeze
   2. The [functools](https://docs.python.org/3/library/functools.html) library makes memoization trivial in Python
   3. Expansion of arrays by duplication is _trivial_ in Python