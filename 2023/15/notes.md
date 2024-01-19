Python's [OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict) is a perfect fit for this problem because:

1. It preserves insertion order
2. It allows in-place updates without changing insertion order
3. Removal of a key results in later insertions "shuffling" forwards
4. Adding a key that was already in the dictionary, but was removed, just appends it to the end
