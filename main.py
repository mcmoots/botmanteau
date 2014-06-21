# "Breakfast presidents" game Twitterbot


import os
import pickle
import punmaker
import pandas
import yaml
import random
from sklearn import preprocessing




class GameRound:
    """ Stuff pertaining to one pair of topics / one day's game round
    """
    def __init__(self, files, rootdir):

        self.pdict = punmaker.PhonemeDictset()
        self.model = pickle.load(open(rootdir+'model.pickle'))
        self.scaler = pickle.load(open(rootdir+'scaler.pickle'))
        self.pca = pickle.load(open(rootdir+'pca.pickle'))
        self.topic1 = yaml.load(open('lists/'+files[0] ))
        self.topic2 = yaml.load(open('lists/'+files[1] ))


    def makeHashtag(self):
        return '#' + self.topic1['Pos1'] + self.topic2['Pos2']


    def openerTweet(self):
        text = self.makeHashtag() + ' is the new #BreakfastPresidents'
        return text


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

        df = pandas.DataFrame(puns)
        model_cols = ['short_strlen', 'long_strlen', 'swscore', 'pct_overlap',
                      'position_beginning', 'position_end']
        # excise any weird results
        df = df[df.pct_overlap < .7]
        df = df[df.pct_overlap >= 0]

        # convert to numpy array
        df = df.convert_objects(convert_numeric=True)
        data = df.as_matrix([model_cols])
        data_scaled = self.scaler.transform(data)
        data_reduced = self.pca.transform(data_scaled)

        dr = pandas.DataFrame(data_reduced)
        df['score'] = [prob[1] for prob in self.model.predict_proba(dr)]
        self.df = df
        return df


    def getTopPuns(self, N):
        '''Return up to N highly-scoring puns'''
        choices = self.df[self.df.score > 0.07]
        if len(choices) < N:
            return choices
        else:
            return choices.ix[random.sample(choices.index, N)]

    def makePunTweet(self, pun):
        '''Tweet a single pun'''
        pass



def main():
    '''Run the bot'''

    # todo: parse argv for root dir
    rootdir = './'

    # todo: import bot API keys

    # choose 2 files from lists dir
    filenames = next(os.walk(rootdir+'lists/'))[2]
    if len(filenames) < 2:
        # todo: tweet a sad tweet and try again tomorrow
        pass

    g = GameRound(random.sample(filenames, 2), rootdir)
    g.makeAllPuns()

    # create & announce hashtag
    tweet = g.openerTweet()

    #


    pass