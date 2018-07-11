#! /usr/bin/python

# Data analysis and wrangling
import pandas as pd
# import numpy as np
# import random as rnd

# Visualization
# import seaborn as sns
# import matplotlib.pyplot as plt
# %matplotlib inline

# Machine learning
from sklearn.linear_model import LogisticRegression
# from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import Perceptron
# from sklearn.linear_model import SGDClassifier
# from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Read Data
data = pd.read_csv('training_sample.csv')
# data2 = pd.read_csv('training_sample2.csv')

# print('COLUMNS: ',data.columns.values)
# data.head()
# data.info()

# Find association between quenching and other parameters
print('-'*30)
print data[["Bar", "Quench"]].groupby(['Bar'], as_index=False).mean().sort_values(by='Quench', ascending=False)
print('-'*30)
# print data[["AGNsed", "Quench"]].groupby(['AGNsed'], as_index=False).mean().sort_values(by='Quench', ascending=False)
# print('-'*30)
print data[["AGNtot", "Quench"]].groupby(['AGNtot'], as_index=False).mean().sort_values(by='Quench', ascending=False)
print('-'*30)
print data[["Morp", "Quench"]].groupby(['Morp'], as_index=False).mean().sort_values(by='Quench', ascending=False)
print('-'*30)
print data[["Mass", "Quench"]].groupby(['Mass'], as_index=False).mean().sort_values(by='Quench', ascending=False)
print('-'*30)
print data[["GFrac", "Quench"]].groupby(['GFrac'], as_index=False).mean().sort_values(by='Quench', ascending=False)
print('-'*30)
# Apply Machine Learning

# LOGISTIC REGRESSION
X = data.drop('Quench',axis=1)
y = data['Quench']

train_X, val_X, train_y, val_y = train_test_split(X, y,random_state=0) # Supplying a numeric value to the random_state argument guarantees we get the same split every time we run this script

# X_test = X_train
# X_test = data2.drop('Quench',axis=1).copy()
train_X.shape, train_y.shape

logreg = LogisticRegression()
logreg.fit(train_X, train_y)
y_pred = logreg.predict(val_X)
acc_log = round(logreg.score(train_X, train_y) * 100, 2)
print('Logistic Regression = ',acc_log)
print('_'*30)

coeff_df = pd.DataFrame(data.columns.delete(0))
coeff_df.columns = ['Feature']
coeff_df["Correlation"] = pd.Series(logreg.coef_[0])
print coeff_df.sort_values(by='Correlation', ascending=False)
print('_'*30)

# # VALIDATE PREDICTION
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_absolute_error

# train_X, val_X, train_y, val_y = train_test_split(X_train, y_train,random_state=0) # Supplying a numeric value to the random_state argument guarantees we get the same split every time we run this script

# dt_model_new = LogisticRegression()
# dt_model_new.fit(train_X,train_y)
predict_prices_new = logreg.predict(val_X)
print('Mean Abs Error NEW = ',mean_absolute_error(val_y,predict_prices_new))


# # RANDOM FOREST
# random_forest = RandomForestClassifier(n_estimators=100)
# random_forest.fit(X_train, Y_train)
# Y_pred = random_forest.predict(X_test)
# random_forest.score(X_train, Y_train)
# acc_random_forest = round(random_forest.score(X_train, Y_train) * 100, 2)
# print('Random Forest = ',acc_random_forest)

