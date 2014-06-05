# "Breakfast presidents" game Twitterbot

import pickle
import punmaker
import pandas
import statsmodels.api as sm


class GameRound:
    """ Stuff pertaining to one pair of topics / one day's game round
    """
    def __init__(self, list1, list2):

        self.pdict = punmaker.PhonemeDictset()
        self.model = pickle.load(open('./model.pickle'))
        # todo: take topic names as args and read in lists from file
        # instead of taking the lists as args
        # self.list1 = etc
        self.list1 = list1
        self.list2 = list2

    def makeAllPuns(self):
        """Generate all possible puns + a predicted score

        Step 1: Generate puns and store their predictive attributes in a data frame
        Step 2: Add a predicted score

        Returns a data frame with all of the scored puns.
        """
        puns = []
        for i1 in self.list1:
            for i2 in self.list2:
                p = punmaker.Portmanteauer(i1, i2, self.pdict)
                pun = p.makePortmanteau()

                if pun is None:
                    continue

                if pun['pct_overlap'] < 0:
                    continue

                if pun['puntype'] == 'beginning':
                    pun['position_beginning'] = 1
                    pun['position_end'] = 0
                elif pun['puntype'] == 'end':
                    pun['position_end'] = 1
                    pun['position_beginning'] = 0
                else:
                    pun['position_end'] = 0
                    pun['position_beginning'] = 1

                pun.pop('puntype')

                puns.append(pun)

        # convert to data frame
        df = pandas.DataFrame(puns)
        model_cols = ['position_end', 'position_beginning', 'short_strlen', 'long_strlen', 'swscore', 'pct_overlap']
        df['score'] = self.model.predict(df[model_cols])

        return df