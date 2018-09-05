#! /usr/bin/python

# cross-validation: run our modeling process on different subsets of the data to get 
# multiple measures of model quality (splits data in different pieces and fits multiple times)

import pandas as pd 
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Imputer
from sklearn.model_selection import cross_val_score

data = pd.read_csv('../2_Random_Forests/melb_data.csv')

cols_to_use = ['Rooms', 'Distance', 'Landsize', 'BuildingArea', 'YearBuilt']

X = data[cols_to_use]
y = data.Price

my_pipeline = make_pipeline(Imputer(),RandomForestRegressor())

scores = cross_val_score(my_pipeline,X,y,scoring='neg_mean_absolute_error',cv=3)
print("The scores are ",-1*scores)
# cv=5 will split the sample in 5 pieces and the testing sample will be 20% of the initial
# cv=3 will split the sample in 3 pieces and the testing sample will be 33.3% of the initial






























