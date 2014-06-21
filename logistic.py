# logistic regression to find scoring for pun candidates

import pandas
import numpy as np
import pylab as pl
from ggplot import *
from sklearn import linear_model, decomposition, datasets
from sklearn.pipeline import pipeline
from sklearn.grid_search import GridSearchCV
import pickle


df = pandas.read_csv('train_breakfast_presidents.csv')
df = df.append( pandas.read_csv('train_fish_sportsballs.csv'), ignore_index=True )
df = df.append( pandas.read_csv('train_beer_novels.csv'), ignore_index=True)
df = df.append( pandas.read_csv('train_tree_countries.csv'), ignore_index=True)
df = df.append( pandas.read_csv('train_cocktail_philosophers.csv'), ignore_index=True)

tdf = pandas.read_csv('test_breakfast_presidents.csv')
tdf = tdf.append( pandas.read_csv('test_scifi_sandwiches.csv'), ignore_index=True )
tdf = tdf.append( pandas.read_csv('test_tree_countries.csv'), ignore_index=True )

# discard pct_overlap < 0 or >70%
df = df[df.pct_overlap >= 0]
df = df[df.pct_overlap < .7]

print ggplot(df, aes('pct_overlap', 'swscore', color='result')) + geom_jitter()

# dummy variables for pun type

dummy_puntype = pandas.get_dummies(df['puntype'], prefix='position')
cols_to_keep = ['short_strlen', 'long_strlen', 'swscore', 'pct_overlap', 'result']

df = df[cols_to_keep].join(dummy_puntype.ix[:, :'position_end'], how='inner')

# convert 'w/l' result categories to 1/0
df.loc[df.result == 'l', 'result'] = 0
df.loc[df.result == 'w', 'result'] = 1

# "object" or bool types will break statsmodels
df = df.convert_objects(convert_numeric=True)

# convert to numpy matrix
data = df.as_matrix(['short_strlen', 'long_strlen', 'swscore', 'pct_overlap',
                     'position_beginning', 'position_end'])
target = df['result']

# Standardize & PCA
scaler = preprocessing.StandardScaler().fit(data)
data_scaled = scaler.transform(data)

pca = decomposition.PCA(n_components='mle')
pca.fit(data_scaled)

data_reduced = pca.transform(data_scaled)

logistic = linear_model.LogisticRegression()
logistic.fit(data_reduced, target)

# save the scaler, PCA, and model
pickle.dump(scaler, open('./scaler.pickle', 'w+'))
pickle.dump(pca, open('./pca.pickle', 'w+'))
pickle.dump(logistic, open('./model.pickle', 'w+'))