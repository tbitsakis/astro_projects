#! /usr/bin/python

# XGBoost is the leading model for working with standard tabular data 
# (the type of data you store in Pandas DataFrames)
# XGBoost is an implementation of the Gradient Boosted Decision Trees algorithm

import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Imputer
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor

data = pd.read_csv('train.csv')

data.dropna(axis=0,subset=['SalePrice'],inplace=True)

y = data.SalePrice
X = data.drop(['SalePrice'],axis=1).select_dtypes(exclude=['object'])

# as_matrix converts the list into an array, so train_X etc are arrays
train_X, test_X, train_y, test_y = train_test_split(X.as_matrix(),y.as_matrix(),test_size=0.25)

my_Imputer = Imputer()
train_X = my_Imputer.fit_transform(train_X)
test_X = my_Imputer.fit_transform(test_X)

my_model = XGBRegressor()
# Add silent=True to avoid printing out updates with each cycle
my_model.fit(train_X, train_y, verbose=False)

predictions = my_model.predict(test_X)
print('_'*80)
print("The MAE is: %f"%mean_absolute_error(predictions,test_y))

# However the XGBoost has some parameters that may dramatically change the result by
# tuning them correctly. Those are:
# 1) n_estimators: specifies how many times to go through the modeling cycle described above
#    early_stopping_rounds: that causes the model to stop iterating when the validation score stops improving

my_model_1 = XGBRegressor(n_estimators=1000)
my_model_1.fit(train_X,train_y,early_stopping_rounds=5,eval_set=[(test_X,test_y)],verbose=False)

predictions_1 = my_model_1.predict(test_X)
print("The MAE is: %f"%mean_absolute_error(predictions_1,test_y))
# Doesn't produce significant change though...

# 2) learning_rate: it stops when the learning rate gets below a value
my_model_2 = XGBRegressor(n_estimators=1000,learning_rate=0.05)
my_model_2.fit(train_X,train_y,early_stopping_rounds=5,eval_set=[(test_X,test_y)],verbose=False)

predictions_2 = my_model_2.predict(test_X)
print("The MAE is: %f"%mean_absolute_error(predictions_2,test_y))
print('_'*80)

# 3) n_jobs: on larger datasets where runtime is a consideration, you can use parallelism to build your 
# models faster. It's common to set the parameter n_jobs equal to the number of cores on your machine

# Compare with AdaBoostRegressor of sklearn
ada_model = AdaBoostRegressor()
ada_model.fit(train_X,train_y)

ada_pred = ada_model.predict(test_X)
print("The MAE for adaboost is: %f"%mean_absolute_error(ada_pred,test_y))

# Compare with RandomForestRegressor of sklearn
rf_model = RandomForestRegressor()
rf_model.fit(train_X,train_y)

rf_pred = rf_model.predict(test_X)
print("The MAE for RF is: %f"%mean_absolute_error(rf_pred,test_y))

# Compare with GradientBoostingRegressor of sklearn which is the closet model
gb_model = GradientBoostingRegressor()
gb_model.fit(train_X,train_y)

gb_pred = gb_model.predict(test_X)
print("The MAE for GBR is: %f"%mean_absolute_error(gb_pred,test_y))












