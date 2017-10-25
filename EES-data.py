#!/usr/bin/env python

"""
This module prepares the EES voter data for analysis. It takes in four Stata 
files (which should reside in the 'data' subdirectory) and produces means and
standard errors of voter placements of the parties by countries. Object names
ending with 89, 94, 99 and 04 indicate surveys in 1989, 1994, 1999 and 2004.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import time
start = time.time()


# EES 1989 data
ees89 = pd.read_stata("data/ZA2320.dta")
countries89 = ['DK', 'FR', 'GER', 'IRE', 'NL', 'GB']  # TODO: single dict.
pos_vars89 = ['var' + str(x) for x in range(203, 213)]
pos_data89 = pd.DataFrame(index=countries89)

for var in pos_vars89:
    ees89[var] = ees89[var].replace({'LEFT': 1, 'RIGHT': 10}, inplace=True)
    pos_data89[var + '_mean'] = ees89.groupby('var003')[var].mean()
    pos_data89[var + '_se'] = ees89.groupby(
        'var003')[var].apply(stats.sem, nan_policy='omit')

del ees89                       # release large Stata file in memory


# EES 1994 data
ees94 = pd.read_stata("data/ZA2865.dta")
countries94_dict = {'DK': 'den', 'FR': 'fra', 'GER': 'wge', 'GB': 'gb',
                    'IRE': 'irl', 'NL': 'net'}
keep_countries = ['DENMARK', 'FRANCE',
                  'WEST GERMANY', 'GB', 'IRELAND', 'NETHERLANDS']
ees94 = ees94.query('country in @keep_countries')
pos_vars94 = ['v' + str(x) for x in range(118, 127)]

# the basic logic of this loop is to collect all means and std.errors
# for one country in the 'pc' pd.Series before appending it to the 
# 'pos_data94' pd.DataFrame.
pos_data94 = pd.DataFrame()
for ckey, cval in countries94_dict.items():
    pc = pd.Series(name=ckey)
    for var in pos_vars94:
        varname = var + '_' + cval
        if varname in ees94.keys():
            ees94[varname] = ees94[varname].replace(
                {'LEFT': 1.0, 'RIGHT': 10, 'DK': None,
                 'NA': None, 99: None}, inplace=True)
            m = pd.Series(ees94[varname].mean(), index=[
                          var + '_mean'], name=ckey)
            se = pd.Series(stats.sem(ees94[varname], nan_policy='omit'), index=[
                           var + '_se'], name=ckey)
            pc = pd.concat([pc, m, se])
    pos_data94 = pos_data94.append(pc)

del ees94


# EES 1999
ees99 = pd.read_stata("data/P1560a.dta")

pos_vars99 = ['var' + str(x) for x in range(118, 130)]
countries99_dict = {'DK': 'Denmark', 'FR': 'France', 'GER': 'Germany', 'GB': 'UK',
                    'IRE': 'Ireland', 'NL': 'Netherlands', 'AT': 'Austria', 'SWE': 'Sweden'}
pos_data99 = pd.DataFrame(index=countries99_dict.values())

for var in pos_vars99:
    ees99[var] = ees99[var].replace({'left': 1, 'right': 10, 'dk': None,
                                     -1.0: None, 'na': None}, inplace=True)
    pos_data99[var + '_mean'] = ees99.groupby('var002')[var].mean()
    pos_data99[var + '_se'] = ees99.groupby(
        'var002')[var].apply(stats.sem, nan_policy='omit')

print('It took', time.time() - start, 'seconds.')
