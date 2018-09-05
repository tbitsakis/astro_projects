#! /usr/bin/python

# The random forest uses many trees, and it makes a prediction by averaging the predictions of each 
# component tree. It generally has much better predictive accuracy than a single decision tree and 
# it works well with default parameters. If you keep modeling, you can learn more models with even 
# better performance, but many of those are sensitive to getting the right parameters. 

import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Loading data
input_file = pd.read_csv('melb_data.csv')

# print(input_file.columns)
input_file = input_file.dropna(axis=0)

y = input_file.Price 
X = input_file[['Rooms', 'Bathroom', 'Landsize', 'BuildingArea', 
               'YearBuilt', 'Lattitude', 'Longtitude']]

# We split the data to train and validation samples
train_X, val_X, train_y, val_y = train_test_split(X,y,random_state=0)

rf_model = RandomForestRegressor()
rf_model.fit(train_X,train_y)

mod_prediction = rf_model.predict(val_X)

print('The mean absolute error is: %d'%mean_absolute_error(val_y,mod_prediction))
# This is actually much better than the DecisionTreeRegressor
print('Top 5 Prices: ')
print(val_y.head())
print('-'*50)
print('Top 5 Predictions:')
print(rf_model.predict(val_X.head()))




