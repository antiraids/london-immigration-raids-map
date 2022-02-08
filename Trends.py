# -*- coding: utf-8 -*
"""
Created on Sun Dec  1 17:41:25 2019

@author: setat
"""

import pandas as pd
import matplotlib.pyplot as plt; plt.style.use('ggplot')
import matplotlib.ticker as mtick
import seaborn as sns; sns.set(); sns.set_palette("bright")
import numpy as np

start = 2014
stop = 2021

# =============================================================================
# Trend lines
# =============================================================================

# Overall trend line gradient
raids = pd.read_csv('AmendedData\\TotalLondonRaidsByYear.csv', index_col=0)
raids = raids[raids['Year'] <= stop]
raids.plot.scatter('Year', 'Count')
m, c = np.linalg.lstsq(np.vstack([raids['Count'], np.ones(len(raids))]).T, raids['Year'])[0]
print('Gradient:',round(m,2))

postcodes = np.unique(raids['Postcode'])

# Individual trend line gradient distribution
raid_trends = pd.DataFrame(columns=['trend'], index=postcodes)
for pc in postcodes:
    pc_data = raids.loc[raids['Postcode']==pc]
    indep = np.vstack([pc_data['Count'], np.ones(len(pc_data))]).T
    dep = pc_data['Year']
    m, c = np.linalg.lstsq(indep, dep)[0]
    raid_trends.loc[pc] = m
raid_trends.plot.hist(legend=False)
plt.title('Distribution of postcode district trends')
plt.xlabel('Trend line gradient')
plt.savefig('Outputs\\PostDistTrendDistribution.png')
raid_trends['trend'].mean()
raid_trends.to_csv('AmendedData\\RaidTrends.csv')

# =============================================================================
# Correlation with ethnicity
# =============================================================================

# Get ethnicity data, format
ethnicity = pd.read_csv(r'AmendedData\\PostcodeEthnicityRates_toplevel.csv')
ethnicity = ethnicity[['postdist', 'total', 'nonwhite_rate']]
ethnicity.columns = ['PostDist', 'Popn', 'NonWhite%']
ethnicity = ethnicity.set_index('PostDist')
print(ethnicity.head())

# Merge with total raid data
raid_total = raids.groupby('Postcode').sum().drop('Year', axis=1)
print(raid_total.head())
raid_ethn = raid_total.join(ethnicity).dropna()
raid_ethn['PostArea'] = raid_ethn.index.str.extract('([a-zA-Z]+)').values
print(raid_ethn.head(1).T)

# Scatter plot coloured by postcode area
fig, ax = plt.subplots(figsize=(8,8))
sns.scatterplot(x="NonWhite%",
                y="Count",
                hue="PostArea",
                size='Popn',
                style='PostArea',
                data=raid_ethn,
                ax=ax
                )
#fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
xticks = mtick.PercentFormatter(xmax=1)
ax.xaxis.set_major_formatter(xticks)
xlbl = "Non-white residents"
ylbl = "# of raids"
ax.set_title('POC % and number of raids')
ax.set_ylabel(ylbl)
ax.set_xlabel(xlbl)
plt.savefig('Outputs\\EthnicityRaidSpread.png')

# Scatter plot with trend lines per postcode area
g = sns.lmplot(x="NonWhite%",
           y="Count",
           hue="PostArea",
           ci=None,
           height=8,
           data=raid_ethn,
           truncate=True
           )
#ticks = g.axes[0][0].get_xticks()
#xlabels = ['{:,.0f}'.format(x) + "%" for x in ticks]
#g.set_xticklabels(xlabels).set_axis_labels(xlbl, ylbl)
#g.xaxis.set_major_formatter(xticks)
plt.savefig('Outputs\\EthnicityRaidSpreadTrendlines.png')

# =============================================================================
# Rate of change over time
# =============================================================================

# Get rate of change data
min_cap = 50
nonsmall_pcs = list(raid_total[raid_total['Count']>=min_cap].index)
rate_change = raids[raids['Postcode'].isin(nonsmall_pcs)].set_index('Postcode')
rate_change['Change'] = np.nan
for pc in nonsmall_pcs:
    for yr in range(start,stop+1):
        yr1 = rate_change.loc[rate_change['Year'] == start]['Count'].loc[pc]
        change = ((rate_change.loc[pc]['Count'] / yr1)*100).tolist()
        rate_change.loc[pc] = rate_change.loc[pc].assign(Change = change)
        total = rate_change.groupby('Postcode').sum().loc[pc, 'Count']
        rate_change.loc[pc, 'Total'] = total
print(rate_change)

# Distribution of % change 2014 to 2021
box = sns.boxplot(x=rate_change[rate_change['Year']==stop]['Change'])
boxticks = box.get_xticks()
boxxlabels = ['{:,.0f}'.format(x) + "%" for x in boxticks]
box.set_xticklabels(boxxlabels)
box.set_xlabel('% change')
box.set_title('Average % change in raids, ' + str(start) + " to " + str(stop))
plt.savefig('Outputs\\PctChange'+str(start)+'-'+str(stop)+'.png')

# Spaghetti plot to show noise
figspag, axspag = plt.subplots(figsize=(8,10))
sns.lineplot(x='Year',
             y='Change',
             hue='Total',
             ci=None,
#             legend=False,
             data=rate_change.reset_index(),
             ax=axspag
             )
axspag.set_xticks(range(start,stop+1))
axspag.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))
axspag.set_ylabel('% change')
axspag.set_title("% change in raids, per postcode district")
plt.savefig('Outputs\\PctChangePerPostDist'+str(start)+'-'+str(stop)+'.png')