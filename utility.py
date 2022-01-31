# Author: William Noonan

from collections import Counter, namedtuple

def is_int(x):
    # Test for int type.
    # Returns True if x is an int, False otherwise
    try:
        int(x)
        return True
    except ValueError:
        return False

def item_counts(iterable, n=None):
    """
    Returns a list of tuples of the n most common elements and their counts, ordered from most to least common.
    :param iterable:
    :param n: Number of tuples to return. Default is all.
    :return: List[tuple
    """
    #Return a list of tuples of the n most common elements and their counts from the most common to the least.
    #If n is omitted or None (default), most_common returns all elements in the counter.
    # Elements with equal counts are ordered arbitrarily. (Source: documentation on collections module.)
    counter = Counter(iterable)
    return counter.most_common(n)


def named_tuple_from_dict(dict, name='NamedTuple'):
    # Creates a named tuple from a dictionary (unpacks dictionary into a named tuple)
    NamedTuple = namedtuple(name, sorted(dict))
    return NamedTuple(**dict)


