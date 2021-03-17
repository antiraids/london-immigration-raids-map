# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 00:27:36 2020

@author: setat
"""

import pandas as pd

df = pd.read_csv('RawData\\KS201EW_Postcode district_Ethnic group.csv')
df.drop(['date', 'geography code', 'Rural Urban'], axis=1, inplace=True)
df.columns = df.columns.str.replace('Ethnic Group: ', '')
df.columns = df.columns.str.replace('measures: Value', '')

df_top = df[[col for col in df.columns if ':' not in col]]
df_top.columns = ['postdist', 'total', 'white', 'mixed',
                  'asian', 'black', 'other']
df_top.set_index('postdist', inplace=True)
df_top['nonwhite_rate'] = df_top.loc[:, 'mixed':'other'].sum(axis=1)
df_top['nonwhite_rate'] = df_top['nonwhite_rate'] / df_top['total']
df_top.to_csv('AmendedData\\PostcodeEthnicityRates_toplevel.csv')

df_subs_cols = ['geography', 'All usual residents; ']
df_subs_cols +=  [col for col in df.columns if ':' in col]
df_subs = df[df_subs_cols]

df_subs = df_subs[['geography', 'All usual residents; ',
                   'White: Other White; ', 'Asian/Asian British: Indian; ',
                   'Asian/Asian British: Pakistani; ',
                   'Asian/Asian British: Bangladeshi; ',
                   'Asian/Asian British: Chinese; ',
                   'Asian/Asian British: Other Asian; ',
                   'Black/African/Caribbean/Black British: African; ',
                   'Black/African/Caribbean/Black British: Caribbean; ',
                   'Black/African/Caribbean/Black British: Other Black; ',
                   'Other ethnic group: Arab; ']]

df_subs.columns = df_subs.columns.str.replace('.*: ', '')
df_subs.columns = df_subs.columns.str.replace(';', '').str.strip()
df_subs.rename(columns={'geography':'postdist',
                        'All usual residents': 'total'}, inplace=True)
df_subs.set_index('postdist', inplace=True)
df_subs.to_csv('AmendedData\\PostcodeEthnicityRates_keylines.csv')
