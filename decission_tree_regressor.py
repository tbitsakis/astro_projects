#! /usr/bin/python

import pandas as pd 
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error

input_file = pd.read_csv('melb_data.csv')

# print(input_file.describe())
# print('-'*50)
# print(input_file.head())
# print('-'*50)
print(input_file.columns)

# Because the file contains NaN values we are going 
# to drop them with the following command
input_file = input_file.dropna(axis=0)

# Now we are going to use the sklearn.tree
# First we have to set the parameters

y = input_file.Price
X = input_file[['Rooms', 'Bathroom', 'Landsize', 
	'BuildingArea','YearBuilt', 'Lattitude', 'Longtitude']]

dt_model = DecisionTreeRegressor()
dt_model.fit(X,y)
# print('-'*50)
# print(dt_model)

# Now we are going to make predictions for the first 5 houses
# in our input file
# print('-'*50)
# print('Making predictions for the following 5 houses:')
# print(X.head())
# print(y.head())
# print('Those are: ')
# print(dt_model.predict(X.head()))
# print('-'*50)

# Now we are going to rate our predictions (using mean_absolute_error MAE)
predict_prices = dt_model.predict(X)
print('Mean Abs Error OLD = ',mean_absolute_error(y,predict_prices))
# However, this is an in-sample score (we used the same data to 
# train and calculate the MAE). This is not correct!

# For this reason is better to split the training sample and use the other
# part for validation. sklearn has train_test_split to do that randomly
from sklearn.model_selection import train_test_split

train_X, val_X, train_y, val_y = train_test_split(X, y,random_state=0) # Supplying a numeric value to the random_state argument guarantees we get the same split every time we run this script

dt_model_new = DecisionTreeRegressor()
dt_model_new.fit(train_X,train_y)
# print('-'*50)
# print(dt_model_new)

print('-'*50)
predict_prices_new = dt_model_new.predict(val_X)
print('Mean price:%d'%val_y.mean())
print('Mean Abs Error NEW = ',mean_absolute_error(val_y,predict_prices_new))

# Now another problem is that the model might over(under)-fit the data
# by using very deep or very shallow trees (leaf nodes).
# In that case we can create a function to estimate the MAE to find the 
# optimal number of leaf nodes
def get_mae(max_leaf_nodes, predictors_train, predictors_val, targ_train, targ_val):
    model = DecisionTreeRegressor(max_leaf_nodes=max_leaf_nodes, random_state=0)
    model.fit(predictors_train, targ_train)
    preds_val = model.predict(predictors_val)
    mae = mean_absolute_error(targ_val, preds_val)
    return(mae)

values = []
print('-'*50)
for max_leaf_nodes in [5, 50, 400, 500, 600, 5000]:
    my_mae = get_mae(max_leaf_nodes, train_X, val_X, train_y, val_y)
    print("Max leaf nodes: %d  \t\t Mean Absolute Error:  %d" %(max_leaf_nodes, my_mae))
    values.append([my_mae,max_leaf_nodes])
# Thus we select the optimal number of leaf nodes to fit our model
min_values = min(values) # finds the min in column 0
best_leaf_nobes = min_values[1]

dt_model_final = DecisionTreeRegressor(max_leaf_nodes=best_leaf_nobes, random_state=0)
dt_model_final.fit(train_X,train_y)
print('-'*50)
print(dt_model_final)

print('-'*50)
print('===== DECISION TREE REGRESSOR METHOD =====')
print('-'*50)
predict_prices_final = dt_model_final.predict(val_X)
print('For %d leaf nodes we predict:'%best_leaf_nobes)
print('mean Abs Error FINAL = ',mean_absolute_error(val_y,predict_prices_final))
print('-'*50)









