# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 00:32:30 2019

@author: setat

Used at https://github.com/setalyas/london-immigration-raids-map
"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import numpy as np

# =============================================================================
# Get the raid data
# =============================================================================

# N
dfN = pd.read_excel(r'RawData\55886 xxx Appendix A.xlsx', skiprows=17)
dfN = dfN.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1)
dfN = dfN.fillna(value=0)
dfN = dfN[dfN['Post Code'].str.startswith('N') == True]
dfN = dfN.set_index('Post Code')
dfN.index.name = 'PostDist'
dfN.head()

# S, with breakdown
dfS = pd.read_excel(r'RawData\57252 xxx Appendix A.xlsx', skiprows=14)
dfS = dfS.drop(['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'], axis=1)
dfS = dfS.iloc[:-10]
dfS.columns = ['PostDist', 2014, 2015, 2016, 2017, 2018, 2019, 'Total']
dfS.set_index('PostDist', inplace=True)
dfS = dfS[dfS.index.str.contains('S[EW]\d', regex=True)]
dfS = dfS.fillna(value=0)
dfS.head()

# E
dfE = pd.read_excel(r'RawData\56323 xxx Annex.xlsx', skiprows=10)
dfE = dfE.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1)
dfE = dfE.fillna(value=0)
dfE = dfE[dfE["Post Codes"].str.startswith('E') == True]
dfE = dfE.set_index("Post Codes")
dfE.index.name = 'PostDist'
#for subpost in ['EC'+str(i) for i in range(1,5)]:
#    _ = dfE.loc[dfE.index.str.startswith(subpost), :].sum()
#    dfE = dfE.drop(dfE.index[dfE.index.str.contains(subpost)])
#    dfE.loc[subpost, :] = _
dfE = dfE.drop('E20') # not worth it - new in 2012, no shp, only 5 raids
dfE = dfE.drop('E19') # not a real postcode
dfE.head()

# W
dfW = pd.read_excel(r'RawData\56325 xxx Annex.xlsx', skiprows=9)
dfW = dfW.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1)
dfW = dfW.dropna()
wrgx = 'W.*\d'
dfW[dfW["Post code and type of address"].str.match(wrgx)].sum() == dfW.iloc[-1]
dfW = dfW[dfW["Post code and type of address"].str.match(wrgx)]
dfW = dfW.set_index("Post code and type of address")
dfW.index.name = 'PostDist'
dfW.columns = [2014, 2015, 2016, 2017, 2018, 2019, 'Total']
dfW.head()

# 2019 ENW
with open('RawData\\57894 PDF scrape_2019RaidsENW.txt','r') as f_open:
    df2019 = f_open.read()
df2019 = df2019.replace('\t', '')
df2019 = df2019.replace('\n\n', '\n')
df2019 = df2019.split('\n')
df2019_postdist = [df2019[i] for i in range(len(df2019)) if i % 2 == 0]
df2019_counts = [df2019[i] for i in range(len(df2019)) if i % 2 == 1]
df2019 = pd.DataFrame(data=[df2019_postdist, df2019_counts]).T
df2019 = df2019[1:] 
df2019.columns = ['PostDist', 2019]
df2019.set_index('PostDist', inplace=True)
df2019.replace('-', 0, inplace=True)
df2019[2019] = pd.to_numeric(df2019[2019])

# 2020 data
df2020 = pd.read_excel(r'RawData\64002 xxx Annex.xlsx', skiprows=10)
df2020 = df2020.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1)
df2020 = df2020.dropna()
df2020.set_index('Post code', inplace=True)
df2020.index.name = 'PostDist'
df2020 = df2020.drop(['Total'])
df2020.head()

# 2021 data
df2021 = pd.read_excel(r'RawData\68195 xxx Annex B.xlsx', skiprows=8)
df2021 = df2021.drop(['Unnamed: 0'], axis=1)
df2021 = df2021.dropna()
df2021.set_index('Postcodes', inplace=True)
df2021.index.name = 'PostDist'
df2021 = df2021.drop(['Total'])
df2021.head()

# =============================================================================
# Prep assisting data
# =============================================================================

# Prep map file
shp = 'RawData\\GB_Postcodes\\PostalDistrict.shp'
map_df = gpd.read_file(shp)
type(map_df) # ooh, different

# Missing postcodes - not worth it, only 5 raids
#new_shps = r'RawData\UK-postcode-boundaries-Jan-2015\Distribution\Districts.shp'
#missing_shps = gpd.read_file(new_shps)
#missing_shps.columns = ['PostDist','geometry']
#missing_pcs = ['E20']  # new postcode area in 2012!
#missing_shps = missing_shps.loc[missing_shps['PostDist'].isin(missing_pcs)]
#map_df = map_df.append(missing_shps, ignore_index=True)

# Assign names to postcode districts
postnames = pd.read_csv('RawData\\PostDistNames.csv', skiprows=1)
postnames = postnames.set_index('PostDist')

# Add EC postcode dist names
ec_pcs = pd.read_csv('RawData\\ECPostDistNames.csv')
ec_pcs = ec_pcs[['Postcode district ', 'Coverage ']]
ec_pcs = ec_pcs.set_index('Postcode district ')
ec_pcs.columns = postnames.columns
ec_pcs.index.name = postnames.index.name
ec_pcs.index = ec_pcs.index.str.strip()
postnames = postnames.append(ec_pcs)

# Population data
popn = pd.read_csv(r'RawData\\Nomis KS101EW usual resident population London.csv')
popn = popn[['geography','Variable: All usual residents; measures: Value']]
popn.columns = ['Postcode','Residents']
popn = popn.set_index('Postcode')

# =============================================================================
# Heavy lifting
# =============================================================================

ldn_raids_by_yr = dfN.append(dfE).append(dfW)
ldn_raids_by_yr.drop(2019, axis=1, inplace=True)
ldn_raids_by_yr = ldn_raids_by_yr.join(df2019)
ldn_raids_by_yr = ldn_raids_by_yr[[2014, 2015, 2016, 2017, 2018, 2019,
                                   'Total', 'Grand Total']]
ldn_raids_by_yr = ldn_raids_by_yr.append(dfS)
ldn_raids_by_yr = ldn_raids_by_yr.join(df2020).join(df2021)
ldn_raids_by_yr = ldn_raids_by_yr[list(range(2014,2022))]
#for col in ldn_raids_by_yr.columns:
#    print(col, '\n', ldn_raids_by_yr[ldn_raids_by_yr[col].isna()])
# Only nulls are ECs for 2019 -- because there were no raids in the data
ldn_raids_by_yr.fillna(0, inplace=True)
ldn_raids_by_yr.to_csv('AmendedData\\LondonRaidsByYear.csv')

yr_by_postdist = ldn_raids_by_yr.T
yr_by_postdist.to_csv('AmendedData\\YearByLondonPostDist.csv')
for cutoff in [50, 100]:
    cutoff_list = yr_by_postdist.sum()[yr_by_postdist.sum()>cutoff].index
    yr_pd_cutoff = yr_by_postdist[list(cutoff_list)]
    cutoff_fp = 'AmendedData\\YearByLondonPostDist_cutoff{}.csv'.format(cutoff)
    yr_pd_cutoff.to_csv(cutoff_fp)
    
for ends in ['N', 'NW', 'E', 'W', 'SE', 'SW']:
    endsrgx = '^{}C?\d'.format(ends)
    ends_list = ldn_raids_by_yr[ldn_raids_by_yr.index.str.contains(endsrgx,
                                                                   regex=True)]
    ends_list = ends_list.index
    yr_pd_ends = yr_by_postdist[list(ends_list)]
    ends_fp = 'AmendedData\\YearByLondonPostDist_{}.csv'.format(ends)
    yr_pd_ends.to_csv(ends_fp)
    

nsew = {'Total': ldn_raids_by_yr}

# for k in nsew.keys():
k = list(nsew.keys())[0]
# strings
raw_exp = 'AmendedData\\' + k + 'LondonRaidsByYear.csv'
shp_exp = 'AmendedData\\' + k + 'LondonPostcodes.shp'
shp_with_data_exp = 'AmendedData\\' + k + 'LondonPostcodesWithData.shp'
shp_with_pop_exp = 'AmendedData\\' + k + 'LondonPostcodesWithDataPopn.shp'
chart_ttl = 'Raids in ' + k + ' London 2014-2019'
chart_rate_ttl = 'Raids per 1000 people in ' + k + ' London 2014-2019'
chart_src = 'Source: Anti-Raids FOI, 2019\n\"the number of immigration raids/visits conducted\"'
map_exp = 'Outputs\\' + k + 'LondonRaids_totalmap.png'
map_rate_exp = 'Outputs\\' + k + 'LondonRaids_ratemap.png'
small_mult_exp = 'Outputs\\' + k + 'LondonRaids_postdistbyyear.png'
small_mult_rate_exp = 'Outputs\\' + k + 'LondonRaids_postdistratebyyear.png'

# Put it into useable formats
df_yr_tot = pd.DataFrame(columns=['Postcode','Year','Count'])
cnt = 0
for pc in nsew[k].index:
    for yr in nsew[k].columns:
        df_yr_tot.loc[cnt] = [pc, yr, nsew[k].loc[pc,yr]]
        cnt += 1
df_yr_tot.head(10)
df_yr_tot.to_csv(path_or_buf=raw_exp)
df_tot = df_yr_tot.groupby('Postcode').sum()

# Filter shape file
area_pc = list(nsew[k].index)
area_map = map_df[map_df['PostDist'].isin(area_pc)]
area_map.plot() # check it's the right shape
area_map.to_file(shp_exp)

# =========================================================================
# Map time, baby
# =========================================================================

# Merge data into map file
merged = area_map.set_index('PostDist').join(df_tot)
merged[['PostArea','Count']] # check
merged.to_file(shp_with_data_exp)

# Putting centre coords into geodf to allow labelling with postdist name later
# merged['coords'] = merged['geometry'].apply(lambda x: x.representative_point().coords[:])
# merged['coords'] = [coords[0] for coords in merged['coords']]
# This no longer worked, and started throwing a ValueError for the tuple coords
# => ditch the static maps that require it too

# Put in popns
local_pop = popn[popn.index.isin(area_pc)]
local_pop.to_csv('AmendedData\\LondonPop.csv')
merged = merged.join(local_pop)
merged['Rate'] = (merged['Count'] / merged['Residents']) * 1000
merged = merged.fillna(0)  # For missing popn data
merged.to_file(shp_with_pop_exp)

# Map - total
# vmin, vmax = 0, (df_tot['Count'].max()//50)*50+50 # chloropleth range
# fig, ax = plt.subplots(1, figsize=(20, 10))
# merged.plot(column='Count', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')
# ax.axis('off')
# ax.set_title(chart_ttl, fontdict={'fontsize': 25, 'fontweight': 3})
# ax.annotate(chart_src, xy=(0.1, .08), xycoords='figure fraction',
#             horizontalalignment='left', verticalalignment='top',
#             fontsize=12, color='#555555')
# for idx, row in merged.iterrows():
#     plt.annotate(idx, xy=row['coords'],
#                  horizontalalignment='center')
# # Create colorbar as a legend
# sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# sm._A = [] # empty array for the data range
# cbar = fig.colorbar(sm) # add the colorbar to the figure
# plt.savefig(map_exp, dpi=300)

# Map - rates
# vmin, vmax = 0, 1 # chloropleth range
# fig, ax = plt.subplots(1, figsize=(20, 10))
# merged.plot(column='Rate', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')
# ax.axis('off')
# ax.set_title(chart_rate_ttl, fontdict={'fontsize': 25, 'fontweight': 3})
# ax.annotate(chart_src, xy=(0.1, .08), xycoords='figure fraction',
#             horizontalalignment='left', verticalalignment='top',
#             fontsize=12, color='#555555')
# for idx, row in merged.iterrows():
#     plt.annotate(idx, xy=row['coords'],
#                  horizontalalignment='center')
# # Create colorbar as a legend
# sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# sm._A = [] # empty array for the data range
# cbar = fig.colorbar(sm) # add the colorbar to the figure
# plt.savefig(map_rate_exp, dpi=300)

# =========================================================================
# Small mults lines
# =========================================================================

# Add names and pops
local_names = postnames[postnames.index.isin(area_pc)]

df_yr = df_yr_tot[~df_yr_tot['Year'].isin(['Total', 'Grand Total'])]
df_yr = df_yr.assign(Name='blank')
for post in local_names.index:
    df_yr.loc[df_yr['Postcode'] == post, 'Name'] = local_names.loc[post, 'Name']
    try:
        df_yr.loc[df_yr['Postcode'] == post, 'Pop'] = local_pop.loc[post,'Residents']
    except:
        df_yr.loc[df_yr['Postcode'] == post, 'Pop'] = np.nan
df_yr['Name'] = df_yr['Postcode'] + ' ' + df_yr['Name']
df_yr['Rate'] = (df_yr['Count'] / df_yr['Pop']) * 1000

wrap_len = int(len(local_names)**0.5)

# Small mults - total
g = sns.relplot(x="Year", y="Count", col="Name",
                kind="line", col_wrap=wrap_len, data=df_yr)
plt.subplots_adjust(top=0.9, bottom=0.1)
plt.suptitle(chart_ttl, x=0.05, y=.95, fontsize = 40,
             horizontalalignment='left', verticalalignment='top')
plt.annotate(chart_src, xy=(0.05, .05), xycoords='figure fraction',
            horizontalalignment='left', verticalalignment='top',
            fontsize=12, color='#555555')
plt.savefig(small_mult_exp)

# Small mults - rate
h = sns.relplot(x="Year", y="Rate", col="Name",
                kind="line", col_wrap=wrap_len, data=df_yr)
plt.subplots_adjust(top=0.9, bottom=0.1)
plt.suptitle(chart_rate_ttl, x=0.05, y=.95, fontsize = 40,
             horizontalalignment='left', verticalalignment='top')
plt.annotate(chart_src, xy=(0.05, .05), xycoords='figure fraction',
            horizontalalignment='left', verticalalignment='top',
            fontsize=12, color='#555555')
plt.savefig(small_mult_rate_exp)