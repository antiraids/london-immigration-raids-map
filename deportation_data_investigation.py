# -*- coding: utf-8 -*-
"""
Created on Sun May 14 13:39:18 2023

@author: setat
"""

import pandas as pd
import matplotlib.pyplot as plt; plt.style.use('ggplot')
import seaborn as sns

fp = 'RawData\\returns-datasets-dec-2022.xlsx'

# =============================================================================
# Get plt parameters to match other graphs, from TellingTheStory
# =============================================================================

plt.rcParams['figure.figsize'] = (15, 11)
plt.rcParams['axes.titlesize'] = 28
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.edgecolor'] = '#A9A9A9'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['savefig.transparent'] = True

watermark_str = "Enforced return data from Gov.uk, covering 2016-2022. More at https://antiraids.github.io"

# =============================================================================
# Get data
# =============================================================================

# Get the right sheet name
xls = pd.ExcelFile(fp)
xls.sheet_names

# Get the data
df = pd.read_excel(fp, sheet_name='Data - Ret_D02', header=1)
df.head(1).T
df_slc = df[df['Return type group'] == 'Enforced return']
df_slc = df_slc[df_slc['Year'] >= 2022]

# =============================================================================
# 2022 data: investigation
# =============================================================================

by_country = df_slc.groupby('Return destination').sum()
by_region = df_slc.groupby('Return destination region').sum()

by_region.sort_values(by='Number of returns')
by_country.sort_values(by='Number of returns')

by_place = df_slc.groupby(['Return destination', 'Return destination region']).sum()
by_place = by_place.reset_index().sort_values('Number of returns')
by_place = by_place[by_place['Number of returns'] >= 20]
by_place.head(2).T
by_place.columns = ['Destination', 'Region', 'Deportations']
by_place['Area'] = by_place['Region'].replace({
    '(^E[uU].*)': 'Europe',
    '.*America Central.*': 'America Central/South',
    '.*Asia South.*': 'Asia South/South East'}, regex=True)
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
sns.barplot(data=by_place, x='Deportations', y='Destination',
            hue='Area', dodge=False, ax=ax)
ax.set_title('Deportations by place', fontsize=25)
ax.annotate('Only includes destinations with >=20 deportations to them. Data\
 from 2022', (0.02, 0.01), xycoords='figure fraction', color='grey',
 fontsize=9)
plt.tight_layout()
plt.savefig('Outputs\\Deportations_by_place_2022.png')

# =============================================================================
# Since 2016, totals
# =============================================================================

df_slc = df[df['Return type group'] == 'Enforced return']
df_slc = df_slc[df_slc['Year'] >= 2016]
by_place = df_slc.groupby(['Return destination', 'Return destination region']).sum()
by_place = by_place.reset_index().sort_values('Number of returns')
by_place = by_place.sort_values('Number of returns').iloc[-20:, :]
by_place.head(2).T
by_place.columns = ['Destination', 'Region', 'Deportations']
by_place['Area'] = by_place['Region'].replace({
    '(^E[uU].*)': 'Europe',
    '.*America Central.*': 'America Central/South',
    '.*Asia.*': 'Asia South/East'}, regex=True)
colorblind_palette = {
    'America Central/South': '#CC79A7',  # blush
    'Asia South/East': '#D55E00',  # burnt
    'Europe': '#009E73',  # green
    'Other': '#000000',  # black
    'Africa Sub-Saharan': '#0072B2'  # blue
        }  # because this is the same order as the legend, this work below too
fig, ax = plt.subplots()
sns.barplot(data=by_place, x='Deportations', y='Destination',
            hue='Area', dodge=False, ax=ax, palette=colorblind_palette.values())
ax.set_title('Top 20 countries deported to since 2016')
ax.set_ylabel('')
plt.annotate(watermark_str, (0.03, 0.03), color='grey', fontsize=15,
             xycoords='figure fraction')
plt.tight_layout()
plt.savefig('Outputs\\Deportations_by_place_2016.png')

# For alt text
for i in by_place.index:
    print(f'{by_place.loc[i, "Destination"]}: {by_place.loc[i, "Deportations"]: .0f}')

# =============================================================================
# Since 2016, by year
# =============================================================================

by_time_20 = df_slc.groupby(['Return destination', 'Return destination region', 'Year']).sum()
by_time_20 = by_time_20.reset_index().sort_values('Number of returns')
by_time_20 = by_time_20[by_time_20['Return destination'].isin(by_place['Destination'])]
by_time_20.head(2).T
by_time_20.columns = ['Destination', 'Region', 'Year', 'Deportations']
by_time_20['Area'] = by_time_20['Region'].replace({
    '(^E[uU].*)': 'Europe',
    '.*America Central.*': 'America Central/South',
    '.*Asia.*': 'Asia South/East'}, regex=True)
by_time_20.sort_values(['Destination', 'Year'], ascending=True, inplace=True)
# Plot on one
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
for c in by_time_20['Destination'].unique():
    to_plot = by_time_20.loc[by_time_20['Destination']==c]
    assert len(to_plot['Region'].unique()) == 1
    a = to_plot['Area'].iloc[0]
    to_plot.plot(x='Year', y='Deportations', c=colorblind_palette[a], ax=ax,
                 legend=None)
ax.set_ylim(0)
ax.set_xlim(2016, 2022)
ax.set_title('Top 20 countries deported to since 2016', fontsize=25)
ax.set_ylabel('Deportations')
ax.set_xlabel('')
top_5 = by_time_20.loc[by_time_20['Year']==2022].nlargest(5, ['Deportations'])
for c in top_5['Destination']:
    yr = 2022
    y = by_time_20.loc[(by_time_20['Destination']==c)&(by_time_20['Year']==yr),
                       'Deportations'].values[0]
    ax.annotate(c, (2022, y), alpha=0.5)
plt.tight_layout()
plt.savefig('Outputs\\Deportations_by_place_2016_by_year.png')
