#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


# EES 1989

ees1989 = pd.read_stata("data/ZA2320.dta")
countries1989 = ['DK', 'FR', 'GER', 'IRE', 'NL', 'GB']  # TODO: single dict.
pos_vars1989 = ['var' + str(x) for x in range(203, 213)]
pos_data1989 = pd.DataFrame()

for var in pos_vars1989:
    ees1989[var] = ees1989[var].replace({'LEFT': 1, 'RIGHT': 10})
    pos_data1989[var + '_mean'] = ees1989.groupby('var003')[var].mean()
    pos_data1989[var + '_se'] = ees1989.groupby(
        'var003')[var].apply(stats.sem, nan_policy='omit')

pos_data1989 = pos_data1989.query('var003 in @countries1989')
del ees1989                     # clear Stata file from memory


# EES 1994 (this dataset has a different structure)

ees1994 = pd.read_stata("data/ZA2865.dta")
countries1994_dict = {'DK': 'den', 'FR': 'fra', 'GER': 'wge', 'GB': 'gb',
                      'IRE': 'irl', 'NL': 'net'}
countries1994 = ['DENMARK', 'FRANCE',
                 'WEST GERMANY', 'GB', 'IRELAND', 'NETHERLANDS']
ees1994 = ees1994.query('country in @countries1994')
pos_vars1994 = ['v' + str(x) for x in range(118, 127)]
pos_data1994 = pd.DataFrame(index=countries1994_dict.keys())

for ckey, cval in countries1994_dict.items():
    for var in pos_vars1994:
        varname = var + '_' + cval
        if varname in ees1994.keys():
            # ees1994[varname] = ees1994[varname].replace(
            #     {'LEFT': 1.0, 'RIGHT': 10, 'DK': None,
            #      'NA': None, 99: None})
            s = pd.Series(ees1994[varname].mean(), name=ckey)
            print(s)
            pos_data1994.append(s)

            # pos_data1994[varname + '_mean'] = ees1994[varname].mean()
            # pos_data1994[varname + '_se'] = stats.sem(
            #     ees1994[varname], nan_policy='omit')
