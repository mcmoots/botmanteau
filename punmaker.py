import numpy
import nltk
import csv
import re
import yaml
from itertools import chain

class PhonemeDictset:
    """Holds a bundle of phoneme/spelling parameters

    Similarity matrix, phoneme spellings, dictionary
    """
    def __init__(self):
        # pronouncing dictionary
        from nltk.corpus import cmudict
        self.dict = cmudict.dict()
        # phoneme similarity matrix
        self.phonesim={}
        with open('arpabet-arbitrary-similarity-matrix.csv') as arp:
            areader = csv.DictReader(arp, delimiter=',', quotechar='"')
            for row in areader:
                self.phonesim[row['Phone']] = row
        # arpabet spellings
        self.arpaspell = yaml.load(open('arpabet_spellings.yaml'))

    def str_to_phones(self, string):
        """Convert string to list of phonemes

        Strategy 1: Look up all the words in the string in self.dict
        If that fails, return an empty list.
        """
        #todo - add a better fallback method
        words = nltk.wordpunct_tokenize(string)
        # CMUdict is ascii-only
        words = [x for x in words if re.match('[a-zA-Z]+', x)]
        phs = []
        try:
            for w in words:
                phs.append(self.dict[w.lower()][0])
                phs.append(['WB'])
        except KeyError:
            return []
        else:
            #strip final 'WB' token
            phs.pop()
            return phs

    def sim_score(self, ph1, ph2):
        """Phoneme similarity score"""
        return float(self.phonesim[ph1][ph2])

    def sw_traceback(self, pointers, phl1, phl2, i, j):
        """ Trace Smith-Waterman alignment scores

        Start at (i, j) in pointer matrix
        """
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

    def sw_match(self, phl1, phl2):
        """Create Smith-Waterman alignment score matrix
        """
        rows = len(phl1) + 1
        cols = len(phl2) + 1
        fmat = numpy.zeros((rows, cols), float)
        pointers = numpy.zeros((rows, cols), float)

        maxScore = [0, 0, 0]    # score, i, j

        for i in range(0,rows):
            fmat[i][0] = 0
        for j in range(0, cols):
            fmat[0][j] = 0

        for i in range(1, rows):
            for j in range(1, cols):
                match = fmat[i - 1][j - 1] + self.sim_score(phl1[i - 1], phl2[j - 1])
                delete = fmat[i - 1][j] + self.sim_score(phl1[i - 1], 'gap')
                insert = fmat[i][j - 1] + self.sim_score('gap', phl2[j - 1])
                fmat[i][j] = max(0, match, delete, insert)

                if (fmat[i][j] == 0):
                    pointers[i][j] = -1
                elif (fmat[i][j] == delete):
                    pointers[i][j] = 1
                elif (fmat[i][j] == insert):
                    pointers[i][j] = 2
                elif (fmat[i][j] == match):
                    pointers[i][j] = 3

                if fmat[i][j] > maxScore[0]:
                    maxScore[0] = fmat[i][j]
                    maxScore[1] = i
                    maxScore[2] = j

        startAlign1 = 1
        startAlign2 = 1

        aphl1, aphl2, startAlign1, startAlign2 = self.sw_traceback(pointers, phl1, phl2, maxScore[1], maxScore[2])

        return aphl1, aphl2, startAlign1, startAlign2, maxScore[0]

    def findPhonemeBreakpoints(self, str, phonemes):
        """Find the point in a string where 2 phonemes might be next to each other
        """

        possible_starts = []
        breakpoints = []

        # Special case for initials & abbreviations
        single_letter = re.compile('(\W|^)(?=(\w(\W|$)))')
        if re.match(single_letter, str):
            # todo single letter workaround
            # get phoneme list for the single letter from CMU dict
            # search it for:
            #   phone1 + phone2 combo (if found, append to breakpoints)
            #   phone1 (if found, append beginning of next word to possible_starts)
            #   phone2 (if found... ????)
            pass


        # Loop through 1st phoneme's possible spellings to find it in 1st string
        # todo - fix for word boundaries
        for spell in self.arpaspell[phonemes[0]]:
            matchexp = '(?=' + spell + ')'
            matchpoints = [m.start() for m in re.finditer(matchexp, str)]
            # special handling for silent e
            if phonemes[0] == 'WB' and spell.startswith('e'):
                possible_starts += [m+1 for m in matchpoints]
            else:
                possible_starts += [m+len(spell) for m in matchpoints]

        #Loop through possible start points to check matches for 2nd phoneme
        for s in possible_starts:
            for spell in self.arpaspell[phonemes[1]]:
                if str[s:].startswith(spell):
                    # more special handling for silent e
                    if phonemes[1] == 'WB' and spell.startswith('e'):
                        breakpoints.append(s+1)
                    else:
                        breakpoints.append(s)

        # if breakpoints == []:
        #     print "Failed to find breakpoint in " + str + ' ' + phonemes[0] + ' ' + phonemes[1]

        return breakpoints

class Portmanteauer:
    """Creates portmanteaux from two strings
    """
    def __init__(self, str1, str2, phonedicts):
        self.str1 = str1
        self.str2 = str2
        self.phonedicts = phonedicts

    def orthographizePun(self, aphl1, aphl2, phl1, phl2, sa1, sa2):
        """Generate a portmanteau from original strings + phoneme alignment

        Examples:   "Grover Cleveland" and "muffin" -> Grover Cmuffind
                    aligned on K [L IY1 V L AH0 N] D / [M AH1 F - AH0 N]

                    "mockingbird" and "bacon" -> baconbird
        Strategy:
            Take the two phonemes that fall across the alignment boundary (K/L, N/D)
            and search for a matching sequence of letters. That is where to split.
        """
        #rename str1/phl1 to str_short & str_long
        if len(phl1) >= len(phl2):
            string_long = self.str1
            aph_long = [ph for ph in aphl1 if ph != '-']
            plist_long = phl1
            sp = sa1
            string_short = self.str2
        else:
            string_long = self.str2
            aph_long = [ph for ph in aphl2 if ph != '-']
            plist_long = phl2
            sp = sa2
            string_short = self.str1
        #todo fail if match did not leave a "tail" on either string

        # Locate splice points in the longer word

        # cases: splice1 = 0 / splice2 = n  - beginning of word
        #       splice1 = n / splice2 = n - middle of word
        #       splice1 = n / splice2 = end of word
        splice1 = 0
        splice2 = 0
        overlap_position = 'error'

        if sp == 0 and sp + len(aph_long) >= len(plist_long):
            return None

        if sp == 0:
            # overlap at beginning of longword
            # in this case we don't want to be greedy about splice2
            overlap_position='beginning'
            splice1 = 0
            splices = self.phonedicts.findPhonemeBreakpoints(string_long,
                                                             [ plist_long[sp + len(aph_long) - 1],
                                                               plist_long[sp + len(aph_long)] ])
            if splices == []:
                return None
            else:
                splice2 = min(splices)
        elif sp + len(aph_long) >= len(plist_long):
            # overlap at end of longword
            # in this case we don't want to be greedy about splice1
            overlap_position='end'
            splice2 = len(string_long)
            splices = self.phonedicts.findPhonemeBreakpoints(string_long, [plist_long[sp-1], plist_long[sp]])
            if splices == []:
                return None
            else:
                splice1 = max(splices)
        else:
            # overlap in the middle
            # we will be greedy and cut out as much of longword as possible.
            overlap_position='middle'
            splices = self.phonedicts.findPhonemeBreakpoints(string_long, [plist_long[sp-1], plist_long[sp]])
            if splices == []:
                return None

            splice1 = min(splices)
            splices = self.phonedicts.findPhonemeBreakpoints(string_long, [ plist_long[sp + len(aph_long) - 1],
                                                                            plist_long[sp + len(aph_long)] ])
            splices = [s for s in splices if s > splice1]

            if splices == []:
                return None
            else:
                splice2 = max(splices)

        # todo - preserve capitalization pattern of long string
        text = string_long[:splice1] + string_short.capitalize() + string_long[splice2:]
        pct_replaced = 1 - ( len(string_long[:splice1]) + len(string_long[splice2:]) ) / float(len(string_long))

        return {
            'pun': text,
            'puntype': overlap_position,
            'pct_overlap': pct_replaced }


    def makePortmanteau(self):
        """Align two phoneme lists
        """
        phl1 = list(chain.from_iterable(self.phonedicts.str_to_phones(self.str1)))
        phl2 = list(chain.from_iterable(self.phonedicts.str_to_phones(self.str2)))

        if phl1 == [] or phl2 == []:
            return None
        aphl1, aphl2, sa1, sa2, score = self.phonedicts.sw_match(phl1, phl2)

        output = self.orthographizePun(aphl1, aphl2, phl1, phl2, sa1, sa2)

        if output is None:
            return None
        else:
            output['short_strlen'] = min([len(self.str1), len(self.str2)])
            output['long_strlen'] = max([len(self.str1), len(self.str2)])
            output['swscore'] = score

        output['str1'] = self.str1
        output['str2'] = self.str2

        return output