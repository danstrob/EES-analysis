#!/usr/bin/env python

"""
This module prepares the EES voter data for analysis. It takes in four Stata
files (which should reside in the 'data' subdirectory) and produces means and
standard errors of voter placements of the parties by countries. Object names
ending with 89, 94, 99 and 04 indicate surveys in 1989, 1994, 1999 and 2004.
"""

import pandas as pd
from scipy import stats


def prep_data(year, data_files, pos_vars, country_var,
              country_dict, replace_dict):
    """
    prep_data is the basic function to read in the Stata files and output
    a pandas data frame with the means and std. errors of party positions.
    Unfortunately the data set for 1994 is structured differently, so the
    function only applies to 1989, 1999, and 2004.
    """
    stata = pd.read_stata('data/' + data_files,
                          columns=pos_vars + [country_var])
    pos_data = pd.DataFrame(index=country_dict.values())
    for var in pos_vars:
        stata[var] = stata[var].replace(replace_dict)
        if year == 2004:  # special recoding for SWE 04
            stata[var] = stata[var].astype(float)
            stata.loc[stata.country == 'sweden',
                      var] = 1 + (stata[var] * 9) / 10

        pos_data[var + '_mean'] = stata.groupby(country_var)[var].mean()
        pos_data[var + '_se'] = stata.groupby(
            country_var)[var].apply(stats.sem, nan_policy='omit')
    return pos_data


data_files = {1989: 'ZA2320.dta',
              1994: 'ZA2865.dta',
              1999: 'P1560a.dta',
              2004: 'ZA4566.dta'}
country_dict = {1989: {'DK': 'DK', 'FR': 'FR', 'GER': 'GER',
                       'IRE': 'IRE', 'NL': 'NL', 'GB': 'GB'},
                1994: {'DK': 'den', 'FR': 'fra', 'GER': 'wge', 'GB': 'gb',
                       'IRE': 'irl', 'NL': 'net'},
                1999: {'DK': 'Denmark', 'FR': 'France', 'GER': 'Germany',
                       'GB': 'UK', 'IRE': 'Ireland', 'NL': 'Netherlands',
                       'AT': 'Austria', 'SWE': 'Sweden'},
                2004: {'DK': 'denmark', 'FR': 'france', 'GER': 'germany',
                       'GB': 'britain', 'IRE': 'ireland', 'NL': 'netherlands',
                       'AT': 'austria', 'SWE': 'sweden'}}
replace_dict = {1989: {'LEFT': 1, 'RIGHT': 10},
                1994: {'LEFT': 1.0, 'RIGHT': 10, 'DK': None,
                       'NA': None, 99: None},
                1999: {'left': 1, 'right': 10, 'dk': None,
                       -1.0: None, 'na': None},
                2004: {'an 11-point scale (0-10) was used in SE': 0.0,
                       'left': 1.0, 'right': 10.0, 'd/k, n/a': None}}
pos_vars = {1989: ['var' + str(x) for x in range(203, 213)],
            1994: ['v' + str(x) for x in range(118, 127)],
            1999: ['var' + str(x) for x in range(118, 130)],
            2004: ['v' + str(x) for x in range(135, 143)]}
country_vars = {1989: 'var003',
                1999: 'var002',
                2004: 'country'}

# run pred_data function for 1989, 1999, and 2004
pos_data = {}
for yr in country_vars.keys():
    pos_data[yr] = prep_data(yr, data_files[yr], pos_vars[yr],
                             country_vars[yr], country_dict[yr],
                             replace_dict[yr])


# EES data set 1994
ees94 = pd.read_stata('data/' + data_files[1994])
keep_countries = ['DENMARK', 'FRANCE',
                  'WEST GERMANY', 'GB', 'IRELAND', 'NETHERLANDS']
ees94 = ees94.query('country in @keep_countries')

# the basic logic of this loop is to collect all means and std.errors
# for one country in the 'pc' pd.Series before appending it to the
# 'pos_data94' pd.DataFrame.
pos_data[1994] = pd.DataFrame()
for ckey, cval in country_dict[1994].items():
    pc = pd.Series(name=ckey)
    for var in pos_vars[1994]:
        varname = var + '_' + cval
        if varname in ees94.keys():
            ees94[varname] = ees94[varname].replace(replace_dict[1994])
            m = pd.Series(ees94[varname].mean(), index=[
                          var + '_mean'], name=ckey)
            se = pd.Series(stats.sem(ees94[varname], nan_policy='omit'),
                           index=[var + '_se'], name=ckey)
            pc = pd.concat([pc, m, se])
    pos_data[1994] = pos_data[1994].append(pc)
