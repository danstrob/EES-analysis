#!/usr/bin/env python

from EESdata import EES_data
import pandas as pd
from numpy import random

party_data = pd.read_csv('data/party_list.csv')
sfb_data = pd.read_csv('data/SFB_output_data.csv')
data = party_data.rename(columns={'country_x': 'country'})
ees_data = EES_data()

# merge party data with voter placements (ees_data):
for year, df in ees_data.items():
    for vars in ['means', 'se']:
        d = ees_data[year].copy().filter(regex=vars)
        d['country'] = d.index
        d['year'] = year
        d = pd.melt(d.rename(columns=lambda x: x.replace('party', '').replace(vars, '')),
                    id_vars=['country', 'year'], value_name=vars, var_name='ees_partynr')
        data = pd.merge(data, d, how='left', on=['year', 'country', 'ees_partynr'])
        xvar, yvar = vars + '_x', vars + '_y'
        if xvar in data.columns:
            data[vars] = data[xvar].fillna(data[yvar])
            data.drop([xvar, yvar], axis=1, inplace=True)

data


cab_data = pd.merge(party_data, sfb_data, on='cab_id')

df = pd.DataFrame(random.poisson(sfb_data['rightMeasures'], size=(10000, len(sfb_data))))
random.poisson(sfb_data['leftMeasures'], size=(10000, len(sfb_data)))

df = df.unstack()
df['cab_id'] = df.index
pd.merge(sfb_data, df.unstack(), on='cab_id')
