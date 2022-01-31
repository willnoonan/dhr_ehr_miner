#AUTHOR: William Noonan
from typing import List
import re
from itertools import chain


def split_strip(string, case=False) -> List[str]:
    """
    Splits a string into pieces delimited by non-word characters and strips them of non-word characters.
    :param string:
    :param case:
    :return:
    """
    nonword_pattern = re.compile(r'[\W]+') # excluding underscore because it doesn't appear in the data and I want to use it to consolidate terms or words
    #xTODO instead of ignoring dashes preceded by particular words, replace these dashes with an underscore (which is a
    # word character) DONE 27-July
    #NOTE: a dash is a nonword character and I want to replace it with white space because it's inconsistently used in the data
    string = nonword_pattern.sub(' ', string) # first replace any nonword characters with a space except those preceded by "non" like non-rheumatic
    return [nonword_pattern.sub('', x.lower()) if not case else nonword_pattern.sub('', x) for x in string.split() if len(nonword_pattern.sub('', x)) > 0]
    # FYI list comprehension faster than generator for small N; avoid generators, they're unnecessary
    # Output is always a list, even if it will just contain a single element


def sublist_splitter(iterable, case=False):
    # Consumes a list of strings, splitting each one into a list of strings using split_strip
    # Returns a list of lists of strings
    return [split_strip(item, case) for item in iterable] # returns a list of lists

def split_and_chain(iterable, case=False):
    # Consumes a list of strings, passes them to sublist_splitter, and chains together its output (a list of lists)
    # Returns a list of strings
    return list(chain.from_iterable(sublist_splitter(iterable, case)))


