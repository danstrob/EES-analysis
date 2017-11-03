#!/usr/bin/env python

"""
This module prepares the EES voter data for analysis. It takes in four Stata
files (which should reside in the 'data' subdirectory) and produces means and
standard errors of voter placements of the parties by countries. Object names
ending with 89, 94, 99 and 04 indicate surveys in 1989, 1994, 1999 and 2004.
The Stata files can be obtained from the official website of the European
Election Studies: http://europeanelectionstudies.net/european-election-studies
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
    df = pd.DataFrame(index=country_dict.keys())
    column_rename_dict = {}

    for i, var in enumerate(pos_vars):
        stata.loc[:, var] = stata.loc[:, var].replace(replace_dict)
        if year == 2004:  # special recoding for SWE 04
            stata.loc[:, var] = stata.loc[:, var].astype(float)
            stata.loc[stata.country == 'sweden',
                      var] = 1 + (stata[var] * 9) / 10

        df.loc[:, var + '_mean'] = stata.groupby(country_var)[var].mean()
        df.loc[:, var + '_se'] = stata.groupby(
            country_var)[var].apply(stats.sem, nan_policy='omit')

        column_rename_dict[var + '_mean'] = 'party' + str(i + 1) + '_mean'
        column_rename_dict[var + '_se'] = 'party' + str(i + 1) + '_se'

    # finally, set unified index and column names
    df = df.rename(country_dict, columns=column_rename_dict)

    return df


def ees_data():
    # define the relevant files, variables and how they should be recoded
    data_files = {1989: 'ZA2320.dta',
                  1994: 'ZA2865.dta',
                  1999: 'P1560a.dta',
                  2004: 'ZA4566.dta'}
    pos_vars = {1989: ['var' + str(x) for x in range(203, 213)],
                1994: ['v' + str(x) for x in range(118, 127)],
                1999: ['var' + str(x) for x in range(118, 130)],
                2004: ['v' + str(x) for x in range(135, 143)]}
    country_vars = {1989: 'var003',
                    1999: 'var002',
                    2004: 'country'}
    country_dict = {1989: {'DK': 'DK', 'FR': 'FR', 'GER': 'GER',
                           'IRE': 'IRE', 'NL': 'NL', 'GB': 'GB'},
                    1994: {'den': 'DK', 'fra': 'FR', 'wge': 'GER', 'gb': 'GB',
                           'irl': 'IRE', 'net': 'NL'},
                    1999: {'Denmark': 'DK', 'France': 'FR', 'Germany': 'GER',
                           'UK': 'GB', 'Ireland': 'IRE', 'Netherlands': 'NL',
                           'Austria': 'AT', 'Sweden': 'SWE'},
                    2004: {'denmark': 'DK', 'france': 'FR', 'germany': 'GER',
                           'britain': 'GB', 'ireland': 'IRE', 'netherlands': 'NL',
                           'austria': 'AT', 'sweden': 'SWE'}}
    replace_dict = {1989: {'LEFT': 1.0, 'RIGHT': 10.0},
                    1994: {'LEFT': 1.0, 'RIGHT': 10.0, 'DK': None,
                           'NA': None, 99.0: None},
                    1999: {'left': 1.0, 'right': 10.0, 'dk': None,
                           -1.0: None, 'na': None},
                    2004: {'an 11-point scale (0-10) was used in SE': 0.0,
                           'left': 1.0, 'right': 10.0, 'd/k, n/a': None}}

    # run pred_data function for 1989, 1999, and 2004
    pos_data = {}
    for yr in country_vars.keys():
        pos_data[yr] = prep_data(yr, data_files[yr], pos_vars[yr],
                                 country_vars[yr], country_dict[yr],
                                 replace_dict[yr])

    # EES dataset 1994
    ees94 = pd.read_stata('data/' + data_files[1994])

    # the basic logic of this loop is to collect all means and std.errors
    # for one country in the 'pc' pd.Series before appending it to the
    # 'pos_data94' pd.DataFrame.
    pos_data[1994] = pd.DataFrame()
    for ckey, cval in country_dict[1994].items():
        pc = pd.Series(name=cval)
        column_rename_dict = {}
        for i, var in enumerate(pos_vars[1994]):
            varname = var + '_' + ckey
            if varname in ees94.keys():
                ees94.loc[:, varname] = ees94[varname].replace(
                    replace_dict[1994])
                m = pd.Series(ees94[varname].mean(), index=[
                              var + '_mean'], name=cval)
                se = pd.Series(stats.sem(ees94[varname], nan_policy='omit'),
                               index=[var + '_se'], name=cval)
                pc = pd.concat([pc, m, se])

            column_rename_dict[var + '_mean'] = 'party' + str(i + 1) + '_mean'
            column_rename_dict[var + '_se'] = 'party' + str(i + 1) + '_se'

        pos_data[1994] = pos_data[1994].append(pc)

    pos_data[1994] = pos_data[1994].rename(
        country_dict, columns=column_rename_dict)

    return pos_data
