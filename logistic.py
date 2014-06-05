# logistic regression to find scoring for pun candidates

import pandas
import statsmodels.api as sm
from ggplot import *
import pickle


df = pandas.read_csv('train_breakfast_presidents.csv')
df = df.append( pandas.read_csv('train_fish_novels.csv'), ignore_index=True )
df = df.append( pandas.read_csv('train_author_cocktails.csv'), ignore_index=True)
df = df.append( pandas.read_csv('train_tree_sandwiches.csv'), ignore_index=True)

print ggplot(df, aes('pct_overlap', 'swscore', color='result')) + geom_jitter()

# dummy variables for pun type

dummy_puntype = pandas.get_dummies(df['puntype'], prefix='position')
cols_to_keep = ['short_strlen', 'long_strlen', 'swscore', 'pct_overlap', 'result']

data = df[cols_to_keep].join(dummy_puntype.ix[:, :'position_end'], how='inner')

# convert 'w/l' result categories to 1/0
data.loc[data.result == 'l', 'result'] = 0.0
data.loc[data.result == 'w', 'result'] = 1.0

# discard pct_overlap < 0
data = data[data.pct_overlap >= 0]

# arbitrary intercept
data['intercept'] = 1.0

# "object" or bool types will break statsmodels
data = data.convert_objects(convert_numeric=True)

train_cols = ['short_strlen', 'long_strlen', 'swscore', 'pct_overlap', 'position_beginning', 'position_end']
logit = sm.Logit(data['result'], data[train_cols])
model = logit.fit()

pickle.dump(model, open('./model.pickle', 'w+'))

