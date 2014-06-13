# Support vector machine classification
import pandas
import numpy
import pickle
from sklearn import svm, datasets, metrics, preprocessing
from sklearn_pandas import cross_val_score


df = pandas.read_csv('train_breakfast_presidents.csv')
df = df.append( pandas.read_csv('train_fish_novels.csv'), ignore_index=True )
df = df.append( pandas.read_csv('train_author_cocktails.csv'), ignore_index=True)
df = df.append( pandas.read_csv('train_tree_sandwiches.csv'), ignore_index=True)

# discard pct_overlap < 0
df = df[df.pct_overlap >= 0]

# convert 'w/l' result categories to 1/0
df.loc[df.result == 'l', 'result'] = 0.0
df.loc[df.result == 'w', 'result'] = 1.0

# dummy variables for pun type
dummy_puntype = pandas.get_dummies(df['puntype'], prefix='position')
cols_to_keep = ['short_strlen', 'long_strlen', 'swscore', 'pct_overlap', 'result']
df = df[cols_to_keep].join(dummy_puntype.ix[:, :'position_end'], how='inner')

# transform into numpy array

df = df.convert_objects(convert_numeric=True)
data = df.as_matrix(['short_strlen', 'long_strlen', 'swscore', 'pct_overlap',
                     'position_beginning', 'position_end'])
target = df['result']

scaler = preprocessing.StandardScaler().fit(data)
data_scaled = scaler.transform(data)

# blackbox for now
clf = svm.SVC(gamma=0.001, C=100.)
model = clf.fit(data_scaled, target)

pickle.dump(clf, open('./model.pickle', 'w+'))
pickle.dump(scaler, open('./scaler.pickle', 'w+'))