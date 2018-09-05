#! /usr/bin/python

# We are going to use Random forests after treating our data null values 
# with 3 different methods
# 1) Drop values
# 2) Imputation: replaces null with some value
# 3) Imputation with missing value prediction

import pandas as pd 
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

# Loading file
input_file = pd.read_csv('../2_Random_Forests/melb_data.csv')

#print(input_file.isnull().sum()) # how many values are null in each column
print('-'*80)

y = input_file.Price

X = input_file.select_dtypes(exclude='object').drop(['Price'],axis=1) # select only numberic predictors and drop "Price"

X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=0.7,test_size=0.3,random_state=0)

def score_dataset(X_train, X_test, y_train, y_test):
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return mean_absolute_error(y_test, preds)

# 1. Get model score from Dropping columns null values
# (we can always drop the lines with null values with input_file = input_file.dropna(axis=0))
cols_with_missing = [col for col in X_train.columns
								 if X_train[col].isnull().any()]

X_train_reduced = X_train.drop(cols_with_missing,axis=1)
X_test_reduced = X_test.drop(cols_with_missing,axis=1)

print("Mean Absolute Error from dropping columns with Missing Values: %f"%
				score_dataset(X_train_reduced, X_test_reduced, y_train, y_test))
print("%d columns used"%len(X_train_reduced.columns))
print('-'*80)

# 2. Get model score from imputation (adds one value to all)
from sklearn.preprocessing import Imputer

my_imputer = Imputer()
X_train_impute = my_imputer.fit_transform(X_train)
X_test_impute = my_imputer.fit_transform(X_test)

print("Mean Absolute Error from Imputation: %f"%
				score_dataset(X_train_impute, X_test_impute, y_train, y_test))
print("%d columns used"%len(X_train.columns))
print('-'*80)

# 3. Get model score from imputation with extra columns showing what was imputed
X_train_impute_plus = X_train.copy()
X_test_impute_plus = X_test.copy()

cols_with_missing = [col for col in X_train.columns
								 if X_train[col].isnull().any()]
for col in cols_with_missing:
	X_train_impute_plus[col + '_was_missing'] = X_train_impute_plus[col].isnull()
	X_test_impute_plus[col + '_was_missing'] = X_test_impute_plus[col].isnull()

my_imputer = Imputer()
X_train_impute_plus = my_imputer.fit_transform(X_train_impute_plus)
X_test_impute_plus = my_imputer.fit_transform(X_test_impute_plus)

print("Mean Absolute Error from Imputation while track what was imputed: %f"%
				score_dataset(X_train_impute_plus, X_test_impute_plus, y_train, y_test))
print("%d columns used"%len(X_train.columns))
print('-'*80)











