#! /usr/bin/python

# Making a pipeline to automatically process our data

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Read Data
data = pd.read_csv('../2_Random_Forests/melb_data.csv')
cols_to_use = ['Rooms', 'Distance', 'Landsize', 'BuildingArea', 'YearBuilt']
X = data[cols_to_use]
y = data.Price
train_X, test_X, train_y, test_y = train_test_split(X, y)


# Making a pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Imputer

my_pipeline = make_pipeline(Imputer(),RandomForestRegressor())

# Use

my_pipeline.fit(train_X,train_y)
predictions = my_pipeline.predict(test_X)

print('The MAE is: %d'%mean_absolute_error(predictions,test_y))





























