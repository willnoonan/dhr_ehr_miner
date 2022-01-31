#AUTHOR: William Noonan
import numpy as np
import pandas as pd
from pandas._testing import rands_array

#Dummy DataFrame with nums
df = pd.DataFrame(np.arange(16).reshape((4,4)), index=['Ohio','Colorado','Utah','Florida'], columns=list('ABCD'))
df = pd.DataFrame(rands_array(6,16).reshape(4,4), index=['Ohio','Colorado','Utah','Florida'], columns=list('ABCD'))

df = pd.DataFrame(np.arange(16).reshape((4,4)), columns=list('ABCD'))
df = pd.DataFrame(rands_array(6,16).reshape(4,4), columns=list('ABCD'))

df=pd.DataFrame([('a','this is a sentence'),('a','this is a word'),('a','get in the car'),
                 ('b','what is this'),('b','is it a dog'),('b','how could you do this'),
                 ('c','it might be a cat'), ('c','is it a cat'),
                 ('d','this is a cat'), ('e', 'it is not a dog')], columns=['one','two'])

#Selecting multiple columns:
df[ df.two > 6].loc[:, 'three':]

#Selecting data with multiple conditions. Use & and |. Must wrap each conditon in paranthesis.
df[ (df['two']>9) | (df['three']>6) ]


#Selecting data where column contains particular strings using regex (case insensitive)
df[df['COMORDES'].str.contains(r"diabetes|hyper", case=False)] # wrap keywords with \b for whole-word only

#Replace values in a column based on a condition:
df.loc[ df.three > 6, 'three' ] = 99 # must use .loc; can't do it this way: df[ df.three > 6].three = 99. This will modify df; a copy is not returned.

#Replace characters in a column:
df.four = df.four.str.replace('LI', '_WOW_') # this was based on what got put into the example df