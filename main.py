# Portmanteau punning algorithm.

# needs to take 2 strings and:
#   convert to phonetic representation (CMU pronouncing dict + ???)
#   calculate "match" score between 2 phoneme strings at given loc.
#   return top-scoring match with the overlap substituted
#       - which term "wins" in this? the shorter one?
#   identify the point in the strings corresponding to the phonemic overlap
#       and construct appropriately overlapped string

# Easy test case: Eggsbraham Lincoln? Porridge Washington?

import csv
import re
import numpy
import nltk
from itertools import chain


params = punmaker.PhonemeDictset()

with open('lists/breakfast.txt') as f:
    breakfast = [line.rstrip('\n') for line in f]

with open('lists/us-presidents.txt') as f:
    presidents = [line.rstrip('\n') for line in f]






