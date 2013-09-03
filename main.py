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

# load cmudict
from nltk.corpus import cmudict
d = cmudict.dict()

def sim_score(str1, str2, smatrix):
    """Phoneme similarity scorer.

    Currently just returns raw value from similarity matrix.
    Maybe someday will do something more sophisticated.
    """
    # checks for input validity should maybe go here.
    return float(smatrix[str1][str2])


def phonemize_string(istr, pdict):
    """Return phonemic representation of a multiword string

    Strategy 1: Look up all words in string in pdict (phonetic dictionary)
    If that fails: Puke a warning.
    Todo: Add a better fallback method.
    """
    words = nltk.wordpunct_tokenize(istr)
    words = [x for x in words if re.match('[a-zA-Z]+', x)]
    phs = []
    try:
        for x in words:
            phs.extend(pdict[x.lower()][0])
    except KeyError:
        print "%s not in dictionary" % x
        return []
    finally:
        return phs


def sw_traceback(pointers, phl1, phl2, i, j):
    """ Trace SW alignment scores 

    Start at i,j in pointer matrix."""
    aseq1 = []
    aseq2 = []

    while pointers[i][j] > 0:
        if pointers[i][j] == 1:
            aseq1.insert(0, phl1[i-1])
            aseq2.insert(0, '-')
            i = i-1
        elif pointers[i][j] == 2:
            aseq1.insert(0, '-')
            aseq2.insert(0, phl2[j-1])
            j = j-1
        elif pointers[i][j] == 3:
            aseq1.insert(0, phl1[i-1])
            aseq2.insert(0, phl2[j-1])
            i = i-1
            j = j-1

    return (aseq1, aseq2, i, j)


def sw_match(phl1, phl2, smat):
    """ create alignment score matrix """
    rows = len(phl1) + 1
    cols = len(phl2) + 1
    fmat = numpy.zeros((rows,cols), float)
    pointers = numpy.zeros((rows, cols), float)

    maxScore = [0, 0, 0]    # score, i, j

    for i in range(0,rows):
        fmat[i][0] = 0
    for j in range(0, cols):
        fmat[0][j] = 0

    for i in range(1, rows):
        for j in range(1, cols):
            match = fmat[i-1][j-1] + sim_score(phl1[i-1],phl2[j-1],smat)
            delete = fmat[i-1][j] + sim_score(phl1[i-1],'gap',smat)
            insert = fmat[i][j-1] + sim_score('gap',phl2[j-1],smat)
            fmat[i][j] = max(0, match, delete, insert)
            
            if(fmat[i][j] == 0):
                pointers[i][j] = -1
            elif(fmat[i][j] == delete):
                pointers[i][j] = 1
            elif(fmat[i][j] == insert):
                pointers[i][j] = 2
            elif(fmat[i][j] == match):
                pointers[i][j] = 3

            if fmat[i][j] > maxScore[0]:
                maxScore[0] = fmat[i][j]
                maxScore[1] = i
                maxScore[2] = j

    startAlign1 = 1
    startAlign2 = 1

    (aphl1, aphl2, startAlign1, startAlign2) = sw_traceback(pointers, phl1, phl2, maxScore[1], maxScore[2])
    return (aphl1, aphl2, startAlign1, startAlign2)

def sw_phones_align(str1, str2, smat):
    """Smith-Waterman alignment of phoneme lists

    """
    phl1 = phonemize_string(str1, d)
    phl2 = phonemize_string(str2, d)
    if phl1==[] or phl2==[]:
        return False
    (aphl1, aphl2, startAlign1, startAlign2) = sw_match(phl1, phl2, smat)
    return (aphl1, aphl2, startAlign1, startAlign2)




# load similarity matrix
arbitrary_sm = {}
with open('arpabet-arbitrary-similarity-matrix.csv') as arp:
    areader = csv.DictReader(arp, delimiter=',', quotechar='"')
    for row in areader:
        arbitrary_sm[row['Phone']] = row
