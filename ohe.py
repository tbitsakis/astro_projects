#! /usr/bin/python

# If we want to use categorical data (e.g. strings) then we can use the One hot enconding
# This method encodes each categorical value with number creating binary columns
# It works well with few (<15) categorical values

# If we want to predict prices of houses using categorical data
import pandas as pd 
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import Imputer

train_data = pd.read_csv('train.csv')
test_data = pd.read_csv('test.csv')

# Drop houses where price is missing
train_data.dropna(axis=0, subset=['SalePrice'], inplace=True)

target = train_data.SalePrice

cols_with_missing = [col for col in train_data.columns
								 if train_data[col].isnull().any()]

# we drop id, and saleprices as well as all columns with null values
candidate_train_predictors = train_data.drop(['Id', 'SalePrice'] + cols_with_missing, axis=1)
candidate_test_predictors = test_data.drop(['Id'] + cols_with_missing, axis=1)

# "cardinality" means the number of unique values in a column
# We use it as our only way to select categorical columns here
low_cardinality_cols = [cname for cname in candidate_train_predictors.columns
										if candidate_train_predictors[cname].nunique<10
										and candidate_train_predictors[cname].dtype == 'object']

numeric_cols = [cname for cname in candidate_train_predictors.columns
								if candidate_train_predictors[cname].dtype in ['int64','float64']]

my_cols = low_cardinality_cols + numeric_cols

train_predictors = candidate_train_predictors[my_cols]
test_predictors = candidate_test_predictors[my_cols]

# For those predictors that are objects we use get_dummies from pandas to one-hot-encode them
one_hot_encoded_training_predictors = pd.get_dummies(train_predictors)

def get_mae(X, y):
	# multiply by -1 to make positive Mean Absolute Error instead of negative value return by sklearn convention
	return -1 * cross_val_score(RandomForestRegressor(50),X,y,scoring='neg_mean_absolute_error').mean()

# we will compare the score with/without dropping the categorical values
predictors_without_categoricals = train_predictors.select_dtypes(exclude=['object'])

mae_without_categoricals = get_mae(predictors_without_categoricals, target)

mae_one_hot_encoded = get_mae(one_hot_encoded_training_predictors, target)

print('-'*80)
print('Mean Absolute Error when Dropping Categoricals: ' + str(int(mae_without_categoricals)))
print('Mean Abslute Error with One-Hot Encoding: ' + str(int(mae_one_hot_encoded)))
print('-'*80)

# So far, you've one-hot-encoded your training data. What about when you have multiple files 
# (e.g. a test dataset, or some other data that you'd like to make predictions for)?  
# Scikit-learn is sensitive to the ordering of columns, so if the training dataset and test datasets 
# get misaligned, your results will be nonsense.  This could happen if a categorical had a different 
# number of values in the training data vs the test data.
# Ensure the test data is encoded in the same manner as the training data with the align command
one_hot_encoded_test_predictors = pd.get_dummies(test_predictors)
final_train, final_test = one_hot_encoded_training_predictors.align(one_hot_encoded_test_predictors,
                                                                    join='left', 
                                                                    axis=1)

# Use RandomForestRegressor and get prediction
my_model = RandomForestRegressor()
my_model.fit(final_train,target)

# print(final_test.isnull().sum()) # I found final_test contain null values and I impute them
# final_test = final_test.dropna(axis=0)
my_imputer = Imputer()
final_test_impute = my_imputer.fit_transform(final_test)
pred = my_model.predict(final_test_impute)
print(pred)












