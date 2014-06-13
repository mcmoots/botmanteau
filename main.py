# "Breakfast presidents" game Twitterbot

import pickle
import punmaker
import pandas
from sklearn import preprocessing


class GameRound:
    """ Stuff pertaining to one pair of topics / one day's game round
    """
    def __init__(self, list1, list2):

        self.pdict = punmaker.PhonemeDictset()
        self.model = pickle.load(open('./model.pickle'))
        self.scaler = pickle.load(open('./scaler.pickle'))
        self.pca = pickle.load(open('./pca.pickle'))
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

                try:
                    pun.pop('puntype')
                    puns.append(pun)
                except ValueError:
                    print i1 + ' ' + i2
                    break

        # convert to data frame
        df = pandas.DataFrame(puns)
        model_cols = ['position_end', 'position_beginning', 'short_strlen', 'long_strlen', 'swscore', 'pct_overlap']
        # convert to numpy array
        df = df.convert_objects(convert_numeric=True)
        data = df.as_matrix([model_cols])
        data_scaled = self.scaler.transform(data)
        data_reduced = self.pca.transform(data_scaled)

        df['score'] = self.model.predict(data_reduced)

        return df