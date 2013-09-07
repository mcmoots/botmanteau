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


def str_to_wordphones(istr, pdict):
    """Return phonemic representation of a multiword string as list of lists

    Strategy 1: Look up all words in string in pdict (phonetic dict)
    If that fails: puke a warning.
    Todo: Add a better fallback method
    """
    words = nltk.wordpunct_tokenize(istr)
    words = [x for x in words if re.match('[a-zA-Z]+', x)]
    phs = []
    try:
        for w in words:
            phs.append(pdict[w.lower()][0])
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

def find_listbounds(nlist):
    """Return list of positions representing a sublist boundary in flattened list
    """
    lens = [len(s) for s in nlist]
    bounds = [0]
    count = 0
    for i in range(len(lens)-1):
        count += lens[i]
        bounds.append(count)
    return bounds
    

def orthographize_pun(str1, str2, pdict, sa1, sa2):
    """Generate a portmanteau from original strings + phoneme alignment position

    Strategy one: Try to align using word boundaries.
    Strategy two: Try to align using naive syllable boundaries.
    """
    words1 = nltk.wordpunct_tokenize(str1)
    words2 = nltk.wordpunct_tokenize(str2)
    phw1 = str_to_wordphones(str1, pdict)
    phw2 = str_to_wordphones(str2, pdict)
    pm = ""
    # Check if start alignment is on word boundary
    b1 = find_listbounds(phw1)
    b2 = find_listbounds(phw2)
    if sa1 in b1 and sa2 in b2 and (sa1 != 0 or sa2 != 0):
        # word boundaries will work!
        if sa1 > sa2: # start with str1, switch to str2
            for i in range(b1.index(sa1)):
                pm += words1[i]
            pm += ' ' + str2
        elif sa2 > sa1: # start with str1, switch to str2
            for i in range(b2.index(sa2)):
                pm += words2[i]
            pm += ' ' + str1
        elif sa1 == sa2:
            print "um wtf i dunno"
    else:
        print "Syllable alignment not written yet, sorry."

    return pm
    


def sw_phones_align(str1, str2, smat, pdict):
    """Smith-Waterman alignment of phoneme lists

    """
    phl1 = list(chain.from_iterable(str_to_wordphones(str1,pdict)))
    phl2 = list(chain.from_iterable(str_to_wordphones(str2,pdict)))
    if phl1==[] or phl2==[]:
        return False
    (aphl1, aphl2, startAlign1, startAlign2) = sw_match(phl1, phl2, smat)
    # split strings into grapheme syllables using vowels
    syl = re.compile('[aeiouy]+[bcdfghjklmnpqrstvwxz]*')
    gm1 = re.findall(syl, str1)
    gm2 = re.findall(syl, str2)
    # check if it worked by comparing to number of vowels in phoneme list
    # arpabet vowels = anything with a digit + 'UW'
    vowph = re.compile('\d')
    v1 = [x for x in phl1 if re.search(vowph, x) or x=='UW']
    v2 = [x for x in phl2 if re.search(vowph, x) or x=='UW']
    if len(gm1) != len(v1):
        print "Warning: English orthography in %s" % str1
    if len(gm2) != len(v2):
        print "Warning: English orthography in %s" % str2
    # Break     
    return (aphl1, aphl2, startAlign1, startAlign2)


# load similarity matrix
arbitrary_sm = {}
with open('arpabet-arbitrary-similarity-matrix.csv') as arp:
    areader = csv.DictReader(arp, delimiter=',', quotechar='"')
    for row in areader:
        arbitrary_sm[row['Phone']] = row
