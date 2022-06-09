# Problem 61:
#     Cyclical Figurate Numbers
#
# Description:
#     Triangle, square, pentagonal, hexagonal, heptagonal, and octagonal numbers
#       are all figurate (polygonal) numbers and are generated by the following formulae:
#
#         Triangle      P[3,n] = n(n+1)/2      1, 3, 6, 10, 15, ...
#         Square	 	P[4,n] = n^2           1, 4, 9, 16, 25, ...
#         Pentagonal    P[5,n] = n(3n−1)/2     1, 5, 12, 22, 35, ...
#         Hexagonal	 	P[6,n] = n(2n−1)       1, 6, 15, 28, 45, ...
#         Heptagonal    P[7,n] = n(5n−3)/2     1, 7, 18, 34, 55, ...
#         Octagonal     P[8,n] = n(3n−2)       1, 8, 21, 40, 65, ...
#
#     The ordered set of three 4-digit numbers: 8128, 2882, 8281, has three interesting properties.
#         1) The set is cyclic, in that the last two digits of each number
#             is the first two digits of the next number (including the last number with the first).
#         2) Each polygonal type:
#             triangle   (P[3,127] = 8128),
#             square     (P[4,91]  = 8281), and
#             pentagonal (P[5,44]  = 2882),
#             is represented by a different number in the set.
#         3) This is the only set of 4-digit numbers with this property.
#
#     Find the sum of the only ordered set of six cyclic 4-digit numbers for which each polygonal type:
#       triangle, square, pentagonal, hexagonal, heptagonal, and octagonal,
#       is represented by a different number in the set.

from collections import defaultdict
from math import ceil, floor, sqrt


# For nicer printing of results
FIGURATE_LABELS = {
    3: 'triangular',
    4: 'square',
    5: 'pentagonal',
    6: 'hexagonal',
    7: 'heptagonal',
    8: 'octagonal',
}

# Parameters of quadratic formulae (a,b) for various figurate numbers
FIGURATE_QUADRATIC_PARAMETERS = {
    3: (0.5,  0.5),  # Triangular:  P[3,n] = n(n+1)/2   = (1/2) * n^2 + (1/2) * n
    4: (1.0,  0.0),  # Square:      P[4,n] = n^2        = (1)   * n^2 + (0)   * n
    5: (1.5, -0.5),  # Pentagonal:  P[5,n] = n(3n−1)/2  = (3/2) * n^2 - (1/2) * n
    6: (2.0, -1.0),  # Hexagonal:   P[6,n] = n(2n−1)    = (2)   * n^2 - (1)   * n
    7: (2.5, -1.5),  # Heptagonal:  P[7,n] = n(5n−3)/2  = (5/2) * n^2 - (3/2) * n
    8: (3.0, -2.0),  # Octagonal:   P[8,n] = n(3n−2)    = (3)   * n^2 - (2)   * n
}


def quadratic_lower_limit(a, b, c):
    """
    Given an inequality of the form:
        a*x^2 + b*x + c >= 0,
        return the integer lower bound (inclusive) for `x`,
        using only the greater of the two quadratic roots,
    NOTE: Assumes that the given formula has real roots.

    Args:
        a (float or int)
        b (float or int)
        c (float or int)

    Returns:
        (int): Integer lower bound (inclusive) for `x`, satisfying the quadratic inequality

    Raises:
        AssertError: if incorrect args are given
    """
    assert type(a) in {float, int}
    assert type(b) in {float, int}
    assert type(c) in {float, int}
    return ceil((-b + sqrt(b**2 - 4*a*c)) / (2*a))


def quadratic_upper_limit(a, b, c):
    """
    Given an inequality of the form:
        a*x^2 + b*x + c < 0,
        return the integer upper bound (exclusive) for `x`,
        using only the greater of the two quadratic roots,
    NOTE: Assumes that the given formula has real roots.

    Args:
        a (float or int): Integer
        b (float or int): Integer
        c (float or int): Integer

    Returns:
        (int): Integer upper bound (exclusive) for `x`, satisfying the quadratic inequality

    Raises:
        AssertError: if incorrect args are given
    """
    assert type(a) in {float, int}
    assert type(b) in {float, int}
    assert type(c) in {float, int}
    return floor((-b + sqrt(b ** 2 - 4 * a * c)) / (2 * a)) + 1


def main():
    """
    Returns the only ordered set of six 4-digit numbers for which the following are true:
      * The set is cyclic, meaning the last two digits of each number is the first two digits of the next number,
          including the last with the first
      * Each polygonal type (triangular, square, pentagonal, hexagonal, heptagonal, and octagonal)
          is represented by a different number in the set

    Returns:
        (List[Tuple[int, int, int]]):
            List where each element represents a number described as above.
            Each element is a tuple of ...
              * The number in the set
              * The polygonal-type, represented as an integer in range [3, 8]
              * The index `n` of that number within the polygon-type's sequence
    """
    global FIGURATE_QUADRATIC_PARAMETERS

    # First, collect all relevant figurate numbers

    # NOTE:
    #     (1) Numbers stored in sets indexed by ...
    #         * (int) Polygon-type as integer in range [3,8]
    #         * (str) Beginning two digits
    #
    #     (2) Numbers stored as tuples of ...
    #         * The number itself
    #         * The polygonal type, represented as an integer in range [3, 8]
    #         * The index `n` of that number within that polygon-type's sequence

    figurate_numbers = dict()
    x_lower_bound = 10 ** 3  # Lower bound (inclusive) of 4-digit numbers
    x_upper_bound = 10 ** 4  # Upper bound (exclusive) of 4-digit numbers

    for m, (a, b) in FIGURATE_QUADRATIC_PARAMETERS.items():
        figurate_numbers[m] = defaultdict(lambda: set())
        n_min = quadratic_lower_limit(a, b, -x_lower_bound)
        n_max = quadratic_upper_limit(a, b, -x_upper_bound)
        for n in range(n_min, n_max):
            x = round(a * n ** 2 + b * n)
            figurate_numbers[m][str(x)[:2]].add((x, m, n))

    # Idea:
    #     Depth-first search through possible sequences,
    #       by incrementally constructing the sequence to satisfy requirements.
    #     Start with octagonal numbers, as these are the fewest.
    #     Try to continue the sequence with new elements by ...
    #       * looking for appropriate starting digits (to remain cyclical), and
    #       * polygons not yet used in current sequence (to use up all polygon types)

    # Local variables to be updated by recursive search
    curr_seq = []
    remaining_polygon_types = set(range(3, 9))

    # Recursive function to execute search
    def search_seqs():
        if len(curr_seq) == len(figurate_numbers):
            # Sequence has been constructed with all previous reqs satisfied
            # Check the last req: whether sequence is fully circular
            return str(curr_seq[-1][0])[2:] == str(curr_seq[0][0])[:2]
        else:
            # Need to add an element to the sequence
            # If starting with empty sequence, try seeding with all octagonal numbers
            ts = {8} if len(curr_seq) == 0 else remaining_polygon_types
            for t in ts:
                if len(curr_seq) == 0:
                    choices = set.union(*figurate_numbers[t].values())
                else:
                    choices = figurate_numbers[t][str(curr_seq[-1][0])[2:]]

                remaining_polygon_types.discard(t)
                for choice in choices:
                    curr_seq.append(choice)
                    if search_seqs():
                        return True  # Found a good sequence, so leave it alone and exit search
                    else:
                        curr_seq.pop()  # Didn't work with this choice, so remove and continue

                # Didn't find any working choice of type `t`, so continue
                remaining_polygon_types.add(t)

            # Nothing worked with `curr_seq`, so step back
            return False

    # Execute the search
    assert search_seqs()

    return curr_seq


if __name__ == '__main__':
    cyclical_figurate_sequence = main()
    print('Cyclical figurate sequence of six 4-digit numbers:')
    for cf_num in cyclical_figurate_sequence:
        print('  {:-10d} = P[{:1d},{:3d}] ({})'.format(*cf_num, FIGURATE_LABELS[cf_num[1]]))
    print('Sum of those numbers:')
    print('  {}'.format(sum(map(lambda cf: cf[0], cyclical_figurate_sequence))))
