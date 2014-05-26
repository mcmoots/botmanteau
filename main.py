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
    # todo - fix what happens w/ unknown word in phrase (test: lemon meringue pie)
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

    return aseq1, aseq2, i, j


def sw_match(phl1, phl2, smat):
    """ create alignment score matrix """
    # todo - return a match score
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

    aphl1, aphl2, startAlign1, startAlign2 = sw_traceback(pointers, phl1, phl2, maxScore[1], maxScore[2])
    return aphl1, aphl2, startAlign1, startAlign2, maxScore[0]

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
    


    
def find_syllable_graphemes(str):
    'Split string into written syllables using vowel-based regex'
    syl = re.compile('(?i)[bcdfghjklmnpqrstvwxz]*[aeiouy]+[bcdfghjklmnpqrstvwxz]*', re.IGNORECASE)
    return re.findall(syl, str)

def sw_phones_align(str1, str2, smat, pdict):
    """Smith-Waterman alignment of phoneme lists

    """
    #todo - add (and penalize) word boundaries
    phl1 = list(chain.from_iterable(str_to_wordphones(str1,pdict)))
    phl2 = list(chain.from_iterable(str_to_wordphones(str2,pdict)))
    if phl1==[] or phl2==[]:
        return False
    aphl1, aphl2, startAlign1, startAlign2, score = sw_match(phl1, phl2, smat)

    print aphl1
    print aphl2

    text = orthographize_pun(str1, str2, aphl1, aphl2, phl1, phl2, startAlign1, startAlign2)
    return text, score


# load similarity matrix
arbitrary_sm = {}
with open('arpabet-arbitrary-similarity-matrix.csv') as arp:
    areader = csv.DictReader(arp, delimiter=',', quotechar='"')
    for row in areader:
        arbitrary_sm[row['Phone']] = row


# load arpabet->spelling table
arpaspell = yaml.load(open('arpabet_spellings.yaml'))


def find_phoneme(ph, d):
    results=0
    tries=0
    while results < 10 and tries < 1000:
        word = random.sample(d,1)[0]
        if ph in list(chain.from_iterable(d[word])):
            print word + str(d[word])
            results += 1
        tries += 1


def find_phoneme_breakpoints(str, phonemes):
    """Find the point in a string where two phonemes might be next to each other
    """
    possible_starts = []
    breakpoints = []
    # Loop through phoneme's possible spellings to find it in first string
    for spell in arpaspell[phonemes[0]]:
        matchexp = '(?=' + spell + ')'
        matchpoints = [m.start() for m in re.finditer(matchexp, str)]
        possible_starts += [m+len(spell) for m in matchpoints]

    # Loop through possible start points for the 2nd phoneme to see if any match
    for s in possible_starts:
        for spell in arpaspell[phonemes[1]]:
            if str[s:].startswith(spell):
                breakpoints.append(s)

    return breakpoints


def orthographize_pun(str1, str2, aph1, aph2, ph1, ph2, sa1, sa2):
    """Generate a portmanteau from original strings + phoneme alignment position

    Examples:   "Grover Cleveland" and "muffin" -> Grover Cmuffind
                aligned on K [L IY1 V L AH0 N] D / [M AH1 F - AH0 N]
                [L IY1 V L AH0 N] [M AH1 F - AH0 N] 6 0

                "mockingbird" and "bacon" -> baconbird
                [M AA1 K IH0 NG] [B EY1 K AH0 N] 0 0

    Strategy:
        Take the two phonemes that fall across the alignment boundary (K/L, N/D)
        and search for a matching sequence of letters. That is where the word is split.

    """
    # rename str1/plist1 & str2/plist2 to str_short & str_long
    if len(ph1) >= len(ph2):
        string_long = str1
        aph_long = [ph for ph in aph1 if ph != '-']
        plist_long = ph1
        sp = sa1
        string_short = str2
    else:
        string_long = str2
        aph_long = [ph for ph in aph2 if ph != '-']
        plist_long = ph2
        sp = sa2
        string_short = str1

    # todo - fail if the match did not leave a "tail" phoneme on either string

    # Locate the following phoneme pairs:
    #   Beginning of substitution in long word
    #   End of substitution in long word

    if sa1 == 0:    # splice at the beginning of the long string
        splice1 = 0
    else:
        splices = find_phoneme_breakpoints(string_long, [plist_long[sp-1], plist_long[sp]])
        if splices == []:
            # ERROR! Throw & handle an exception?
            print "Failed to find spelling in " + string_long + ' ' + plist_long[sp-1] + ' ' + plist_long[sp]
            return None
        else:
            splice1 = min(splices)

    if sa1 + len(aph_long) >= len(plist_long):  # do not use end part of long word
        splice2 = len(plist_long) + 1
    else:
        splices = find_phoneme_breakpoints(string_long,
                                           [ plist_long[sa1+len(aph_long)-1], plist_long[sa1+len(aph_long)] ])
        if splices == []:
            print "Failed to find spelling in " + string_long + ' ' + plist_long[sa1+len(aph_long)-1] +     \
                    ' ' + plist_long[sa1+len(aph_long)]
            return None
        splice2 = max(splices)

    # Build string as following:
    #   string_long[:1st_splice_long] + string_short + string_long[2nd_splice_long:]
    return string_long[:splice1] + string_short + string_long[splice2:]
