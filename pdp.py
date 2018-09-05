#! /usr/bin/python

# Partial dependence plots show how each variable or predictor affects the model's predictions
# The partial dependence plot is calculated only after the model has been fit

from sklearn.ensemble.partial_dependence import partial_dependence, plot_partial_dependence
from sklearn.preprocessing import Imputer
import pandas as pd 
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
import matplotlib.pyplot as plt

cols_to_use = ['Distance', 'Landsize', 'BuildingArea']

def get_some_data():
	data = pd.read_csv('../2_Random_Forests/melb_data.csv')
	y = data.Price
	X = data[cols_to_use]
	my_imputer = Imputer()
	imputed_X = my_imputer.fit_transform(X)
	return imputed_X,y

X,y = get_some_data()

my_model = GradientBoostingRegressor()
my_model.fit(X,y)
# print(my_model)

my_plots = plot_partial_dependence(my_model,
								   features=[0,1,2],
								   X=X,
								   feature_names=cols_to_use,
								   grid_resolution=10)
plt.show(my_plots)

































