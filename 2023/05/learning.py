# Adapted from https://github.com/b-locke/aoc-23/blob/main/day-5-pt-2.py
# I really liked this person's approach for a number of reasons:
# 1) It's remarkably compact when comments are removed, yet still understandable code
# 2) It's super-efficient and runs extremely quickly even for large input
# 3) It doesn't resort to reverse-lookup, root-finding/binary-search, or approximations etc

# I've heavily commented the code to aid with understanding.
# I've also made a couple of optimisations and removed a redundancy I spotted (trivial changes).
import pathlib

# Split file into chunks delimited by two newline markers
file_name = "input_small"
puzzle_input = pathlib.Path(file_name).read_text().split('\n\n')
# Create a list of lists - each top-level list represents a section from the file
# Each sub-list is all the rows inside the section
puzzle_input = [line.strip().split('\n') for line in puzzle_input]
# puzzle_input now contains 8 elements.
# Element 0 contains the seed information
# Elements 1 to 7 contain the maps


def seed_locations(lines):
    # Extract the list of seeds from the first section
    seed_list = [int(seed) for seed in lines[0][0].split(':')[1].split()]
    # Create a list of lists - each list item is a 2-element list containing the start and end of the seed range
    seeds = [[seed_list[a], seed_list[a] + seed_list[a + 1] - 1] for a in range(0, len(seed_list), 2)]
    # Everything after the seeds declaration (element 0) is a map
    maps = lines[1:]
    # Loop over each map in order
    for m in maps:
        i = 0
        # For each seed range, see if we can find an intersection with the current map
        # Note: len(seeds) can, and typically will, increase as the algorithm runs.
        # Therefore len(seeds) will return increasing values until all seed ranges (and possible splits)
        # have been found and mapped for the current map (m)
        while i < len(seeds):
            # Tracks if we have found an intersection of the seed range with the current map
            f = False
            seed_start, seed_end = seeds[i]
            # Element 0 of the map contains header info, so only elements 1 onwards contain the mapping data
            for line in m[1:]:
                # Unpack(destructure) the 3 values (destination, source, range) from the current line
                d, s, r = [int(x) for x in line.split()]

                # Does the start of the seed range intersect with the current map line source range?
                # i.e. is seed_start ∈ [s, s + r) ?
                if s <= seed_start < (s + r) and f is False:
                    # Record that we found an intersection
                    f = True
                    # Replace the start of the seed range with the mapped destination value
                    seeds[i][0] = d + (seed_start - s)
                    # Does the end of the seed range intersect with the current map line?
                    # i.e. is seed_end ∈ [s, s + r) ?
                    if seed_end < s + r:
                        # Replace the end of the seed range with the mapped destination value
                        seeds[i][1] = d + (seed_end - s)
                    else:
                        # The end of the seed range is larger than the end of the current map line source range.
                        # First, we replace the end of the seed range with
                        # the end of the mapped destination of the current map line.
                        # i.e. seed_end -> d + r -1
                        seeds[i][1] = d + r - 1
                        # Second, we add a new seed range that spans from just past the end of
                        # the current map line source range up to seed_end
                        # i.e. add a new seed range [s + r, seed_end]
                        seeds.append([s + r, seed_end])
                        # This has effectively split the initial seed range
                        # i.e. [seed_start, seed_end] ->
                        #     [d + (seed_start - s), d + r -1], (mapped)
                        #     [s + r, seed_end] (un-mapped)

                        # Question: Why use the source values and not the destination values for the second range?
                        # Answer: Because we can't yet know if these seed values will end up being mapped.
                        # So we split the initial seed range into mapped and un-mapped pairs and rely
                        # on later passes of the for loop to perform the mapping of un-mapped pairs.
                        # In the special case where there is no intersection then the mapping is simply 1-1.

                # The start of the seed range did not intersect the current map line source range.
                # Does the end of the seed range intersect with the current map line source range?
                # i.e. is seed_end ∈ [s, s + r) ?
                elif s <= seed_end < (s + r) and f is False:
                    # Record that we found an intersection
                    f = True
                    # Replace the end of the seed range with the mapped destination value
                    seeds[i][1] = d + (seed_end - s)

                    # The start of the seed range is less than the start of the current map line source range.
                    # However, the end of the seed range intersects the current map line source range.
                    # First, we replace the start of the seed range with the start of the current map line
                    # destination range.
                    seeds[i][0] = d
                    # Second, we add a new seed range that spans from seed_start up to just before the
                    # start of the current map line source range
                    # i.e. add a new seed range [seed_start, s -1]
                    seeds.append([seed_start, s - 1])
                    # This has effectively split the initial seed range
                    # i.e. [seed_start, seed_end] ->
                    #     [seed_start, s - 1], (un-mapped)
                    #     [d, d + (seed_end - s)] (mapped)

                    # Question: Why use the source values and not the destination values for the first range?
                    # Answer: Because we can't yet know if these seed values will end up being mapped.
                    # So we split the initial seed range into mapped and un-mapped pairs and rely
                    # on later passes of the for loop to perform the mapping of un-mapped pairs.
                    # In the special case where there is no intersection then the mapping is simply 1-1.

                if f is True:
                    # We have successfully mapped the current seed range so move on to the next seed range.
                    break

            # Proceed to the next seed range
            i += 1

    # At this point we have accumulated the seed ranges (splitting where required) and
    # converted them to mapped location ranges via the intermediate maps.
    # Therefore, seeds now contains pairs of [start, end] location values.
    # Since pairs of locations must be monotonically increasing the start holds the minimum value for each pair.
    # To further understand this statement, the maps are piecewise linear transforms that are monotonically increasing
    # therefore the start of any mapped range must be the minimum for the range.

    # To find the minimum location we need to find the minimum value of each [start, end] pair (i.e. start)
    # and then find the global minimum over all of these.
    return min(s[0] for s in seeds)


output = seed_locations(puzzle_input)
print(f"Part 2: {output}")
