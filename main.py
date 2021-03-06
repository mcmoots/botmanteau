# "Breakfast presidents" game Twitterbot

import sys
import os
import pickle
import twitter
import punmaker
import pandas
import yaml
import random
from time import sleep


class GameRound:
    """ Stuff pertaining to one pair of topics / one day's game round
    """
    def __init__(self, files, rootdir):

        self.pdict = punmaker.PhonemeDictset(rootdir)
        self.model = pickle.load(open(rootdir + 'model.pickle'))
        self.scaler = pickle.load(open(rootdir + 'scaler.pickle'))
        self.pca = pickle.load(open(rootdir + 'pca.pickle'))
        self.topic1 = yaml.load(open(rootdir + 'lists/'+files[0] ))
        self.topic2 = yaml.load(open(rootdir + 'lists/'+files[1] ))

        self.list1 = self.topic1['Items']
        self.list2 = self.topic2['Items']


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

        # delete unneeded columns
        del_cols = ['short_strlen', 'long_strlen', 'swscore', 'pct_overlap', 'position_beginning', 'position_end']
        df = df.drop(del_cols, 1)

        self.df = df
        return df


    def getTopPuns(self, N):
        '''Return up to N highly-scoring puns'''
        choices = self.df[self.df.score > 0.07]
        if len(choices) < N:
            return choices
        else:
            return choices.ix[random.sample(choices.index, N)]



def run_bot(rootdir):
    '''Run the bot'''

    tokens = yaml.load(open(rootdir + 'config.yaml'))
    api = twitter.Api(**tokens)

    # choose 2 files from lists dir
    filenames = next(os.walk(rootdir+'lists/'))[2]
    if len(filenames) < 2:
        sad_text = "I can't find my topic lists :["
        api.PostUpdate(sad_text)
        error_text = "Not enough lists found in " + rootdir + 'lists/'
        sys.exit(error_text)


    for tries in range(0,4):
        topics = random.sample(filenames, 2)
        g = GameRound(topics, rootdir)
        open_text = g.openerTweet()
        try:
            api.PostUpdate(open_text)
            break
        except TwitterError as e:
            print "TwitterError: {0} ({1}) for {2} {3}".format(e.message, e.code, topics[0], topics[1])
            sleep(10)

        if tries == 3:
            sad_text = "Not feeling very creative today. :["
            api.PostUpdate(sad_text)
            sys.exit()

    g.makeAllPuns()

    # tweets!
    puns = g.getTopPuns(12)

    for p in puns.iterrows():
        text = p[1][0].title() + ' ' + g.makeHashtag()
        api.PostUpdate(text)
        sleep(7200)



# run the bot
if __name__ == '__main__':
    if len(sys.argv) > 1:
        rootdir = sys.argv[1]
    else:
        rootdir = './'

    run_bot(rootdir)
