# Part 1

We can think of each workflow `w` as a function that maps a part `p` to a result `x` i.e. 

```text
w(p) => x, where x in {A, R}
```

The function `w` contains `n` steps, `s_1`, ..., `s_n`.

To evaluate the steps of `w`, we process them in order and return the result of the first matching step.

# Part 2

The solution used for part 1 is not going to work due to there being too many possible distinct combinations.

```text
Total combinations = 4000^4 = 256000000000000
```

But there is at least one other way to represent this problem.

The domain of the problem is 4 dimensional space with dimensions `x, m, a, s`.
Each dimension can take values in the range `[1, 4000]`.

Using the workflows we can partition the problem domain into bounded subdomains that will either accept or reject points inside that subdomain.

Therefore, a solution approach is as follows:

1. Start with the full problem domain and partition it into subdomains using the workflows
2. After this is done we will have a finite set of subdomains that will be labelled either accept `A` or reject `R`
3. Compute the volume `V` for each rejected subdomain, where the volume is given by the size of each dimension in the subdomain
4. Subtract all rejected volumes from the total possible combinations to yield the number of accepted points in the problem domain
