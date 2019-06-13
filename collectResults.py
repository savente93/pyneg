from pandas import Series, DataFrame
import pandas as pd
import os


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

results = DataFrame()

for file in os.listdir('../logs'):
	# print(file)
	# print(pd.read_csv(os.path.join('../logs',file),index_col=0))
	results = pd.concat([results,pd.read_csv(os.path.join('../logs',file),index_col=0)],axis=1)

print(results.T)