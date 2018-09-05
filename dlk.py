#! /usr/bin/python

# Data leakage is a serious bias we should take care to have accurate model predictions
# There are two main types of leakage: 
# Leaky Predictors: when your predictors include data that will not be available at the time you make predictions
# To prevent this type of data leakage, any variable updated (or created) after the target value is realized 
# should be excluded. Because when we use this model to make new predictions, that data won't be available to the model.
# Leaky Validation Strategies: e.g. fitting the Imputer for missing values before calling train_test_split
# Never fit validation data with any of the preprocessing procedures!!!


# To verify model ACCURACY we have:
import pandas as pd 
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

data = pd.read_csv('AER_credit_card_data.csv',
					true_values=['yes'],
					false_values=['no'])
print(data.shape)

y = data.card
X = data.drop(['card'],axis=1)

my_pipeline = make_pipeline(RandomForestClassifier())
cv_scores = cross_val_score(my_pipeline,X,y,scoring='accuracy')
print('-'*80)
print('Cross val accuracy: %f percent'%cv_scores.mean())
# The accuracy is very high, something is going wrong!

# A few variables look suspicious. For example, does expenditure mean expenditure on this card or on cards 
# used before appying?

expenditures_cardholders = data.expenditure[data.card]
expenditures_noncardholders = data.expenditure[~data.card]

print('-'*80)
print('Fraction of those who received a card with no expenditures: %.2f' \
      %(( expenditures_cardholders == 0).mean()))
print('Fraction of those who received a card with no expenditures: %.2f' \
      %((expenditures_noncardholders == 0).mean()))
print('-'*80)
# This seems a data leak, where expenditures probably means expenditures on the card they applied for

# To run the model without leaks
potential_leaks = ['expenditure', 'share', 'active', 'majorcards']
X2 = X.drop(potential_leaks, axis=1)
cv_scores = cross_val_score(my_pipeline, X2, y, scoring='accuracy')
print("Cross-val accuracy: %f percent" %cv_scores.mean())
print('-'*80)
# Indeed to accuracy has decreased













