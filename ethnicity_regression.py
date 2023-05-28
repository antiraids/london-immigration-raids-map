# -*- coding: utf-8 -*-
"""
Created on Sat May 13 16:55:29 2023

@author: setat
"""

import arviz as az
import bambi as bmb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.style.use('ggplot')
import seaborn as sns
from scipy.stats import boxcox
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler, RobustScaler

ethn = pd.read_csv('AmendedData\\PostcodeEthnicityRates_keylines.csv',
                   index_col=['postdist'])
raid = pd.read_csv('AmendedData\\PopnRaidsRate.csv', index_col=['Postcode'])

ethn.head()
ethns = ethn.iloc[:, 1:].columns
# Make counts into rates
for col in ethns:
    ethn[col] = ethn[col] / ethn['total']
    
raideth = raid.join(ethn)
na_check = raideth[raideth.isna().any(axis=1)]
assert (na_check['Residents'] < 5000).all()  # check all NAs are weird postdist
raideth.dropna(inplace=True)

scalex = MinMaxScaler()
X_scaled = scalex.fit_transform(raideth[ethns])

# Scale x, leave y
y = raideth['Rate']
model = LinearRegression()
model.fit(X_scaled, y)
print(model.score(X_scaled, y), model.intercept_)
for e, c in zip(ethns, model.coef_):
    print(f'{e}: {c:.2f}')

# Scale x, robust-scale y
scaley = RobustScaler()
y_scaled = scaley.fit_transform(raideth['Rate'].array.reshape(-1, 1))
model = LinearRegression()
model.fit(X_scaled, y_scaled)
print(model.score(X_scaled, y_scaled), model.intercept_)
for e, c in zip(ethns, model.coef_[0]):
    print(f'{e}: {c:.2f}')
    
# Bambi
df_scaled = pd.DataFrame(X_scaled)
df_scaled.columns = [e.replace(" ", "") for e in ethns]
df_scaled['raids_per_k'] = raideth['Rate'].values
df_scaled.head(1).T

model = bmb.Model("raids_per_k ~ OtherWhite + Indian + Pakistani + Bangladeshi\
+ Chinese + OtherAsian + African + Caribbean + OtherBlack + Arab", df_scaled)
fitted = model.fit()
az.summary(fitted)
az.plot_trace(fitted)
summary = az.summary(fitted)
summary.to_csv('AmendedData\\bambi_summary_naive.csv')

# i.e. residuals had mean 45 w/ SD 2.8, intercept was -44 SD 15
# "OtherWhite" had the strongest contribution (160 SD 29) with all others
# basically around the levels of noise
# => if there were two areas, ceteris paribus, then every 10% of 'OtherWhite'
# residents would drive 16 more raids (+/- 3)

az.plot_pair(raideth[ethns].to_dict("list"),
             marginals=True,
             textsize=24);

# =============================================================================
# Transformation attempts
# =============================================================================

transforms = {'reciprocal': -1,
              'reciprocal sqrt': -0.5,
              'log': 0,
              'sqrt': 0.5,
              'none': 1}
for k, v in transforms.items():
    figs, axs = plt.subplots(2, 5, figsize=(12, 5), sharex=True)
    for e, ax in zip(ethns + ['Count', 'Rate'], axs.flatten()):
        ax.hist(boxcox(raideth[e] + 1, v))
        ax.set_title(e)
    plt.suptitle(f'Ethnicity %s by region (transform: {k})', fontsize=25)
    plt.tight_layout()
    plt.savefig(f'Outputs\\ethn_spread_{k}.png')
    plt.show()

# Let boxcox optimise itself, save the variable in case want to reverse
boxcoxs = dict()
figs, axs = plt.subplots(2, 5, figsize=(12, 5), sharex=True)
for e, ax in zip(ethns, axs.flatten()):
    eth_trans = boxcox(raideth[e] + 1)
    ax.hist(eth_trans[0])
    ax.set_title(e)
    boxcoxs[e] = {'data': eth_trans[0], 'lambda': eth_trans[1]}
plt.suptitle('Ethnicity %s by region (transform: boxcox)', fontsize=25)
plt.tight_layout()
plt.savefig('Outputs\\ethn_spread_boxcox.png')

# Recheck modelling
model = LinearRegression()
scalex = MinMaxScaler()
X_scaled = scalex.fit_transform(pd.DataFrame([boxcoxs[e]['data']
                                              for e in ethns]).T)
model.fit(X_scaled, y)
print(model.score(X_scaled, y), model.intercept_)
for e, c in zip(ethns, model.coef_):
    print(f'{e}: {c:.2f}')
# Looks plausible => train Bambi

# Bambi
df_scaled = pd.DataFrame(X_scaled)
df_scaled.columns = [e.replace(" ", "") for e in ethns]
df_scaled['raids_per_k'] = raideth['Rate'].values
df_scaled.head(1).T

model = bmb.Model("raids_per_k ~ OtherWhite + Indian + Pakistani + Bangladeshi\
+ Chinese + OtherAsian + African + Caribbean + OtherBlack + Arab", df_scaled)
fitted = model.fit()
az.summary(fitted)
az.plot_trace(fitted)
summary2 = az.summary(fitted)
summary2.to_csv('AmendedData\\bambi_summary_boxcox.csv')

# Check out the sd comparison
summary[['sd']].join(summary2['sd'], rsuffix='2')
# Mostly constrains the sds down, as expected!

posterior_predict = model.predict(fitted, kind="pps")
az.plot_ppc(fitted)

# =============================================================================
# Plot estimates
# =============================================================================

fig, axs = plt.subplots(2, 1, sharex=True, figsize=(8, 8))
for summ, t, ax in zip([summary, summary2], ['Naive', 'Box-Cox'], axs):
    sns.pointplot('mean', summ.index, data=summ,
                  dodge=True, join=False, ci=None, ax=ax)
    # Get points, to use for error bars
    x_coords = []
    y_coords = []
    for point_pair in ax.collections:
        for x, y in point_pair.get_offsets():
            x_coords.append(x)
            y_coords.append(y)
    ax.errorbar(x_coords, y_coords, xerr=(1.96*summ['sd']).values, fmt=' ')
    ax.set_title(f'Regression estimates ({t})')
plt.savefig('Outputs\\ethn_regr_coefs.png')

# =============================================================================
# Obvious issues
# =============================================================================

# 1. Most raids_per_k values are <5/1000
df_scaled['raids_per_k'].describe()
df_scaled['raids_per_k'].sort_values().clip(0, 70).hist()
# 2. Many of the raids_per_k outliers are small places:
raideth[raideth['Residents'] < raideth['Residents'].quantile(0.2)]
raideth[raideth['Residents'] > raideth['Residents'].quantile(0.2)]['Rate'].hist()

# =============================================================================
# 
# =============================================================================

raideth_trim = raideth[raideth['Residents'] > raideth['Residents'].quantile(0.2)].copy()

to_boxcox = list(ethns) + ['Count', 'Rate']
boxcox_trim = dict()
figs, axs = plt.subplots(3, 4, figsize=(8, 5))
for e, ax in zip(to_boxcox, axs.flatten()):
    eth_trans = boxcox(raideth_trim[e] + 1)
    ax.hist(eth_trans[0])
    ax.set_title(e)
    boxcox_trim[e] = {'data': eth_trans[0], 'lambda': eth_trans[1]}
plt.suptitle('Ethnicity %s by region (transform: boxcox)', fontsize=25)
plt.tight_layout()
plt.savefig('Outputs\\ethn_trim_spread_boxcox_inc_rate.png')

# Recheck modelling
model = LinearRegression()
scalex = MinMaxScaler()
X_scaled = scalex.fit_transform(pd.DataFrame([boxcox_trim[e]['data']
                                              for e in ethns]).T)
y_scaled = boxcox_trim['Rate']['data']
model.fit(X_scaled, y_scaled)
print(model.score(X_scaled, y_scaled), model.intercept_)
for e, c in zip(ethns, model.coef_):
    print(f'{e}: {c:.2f}')
# Hm. Different!

# Bambi
df_scaletrim = pd.DataFrame(X_scaled)
df_scaletrim.columns = [e.replace(" ", "") for e in ethns]
df_scaletrim['raids_per_k'] = boxcox_trim['Rate']['data']
df_scaletrim.head(1).T

model3 = bmb.Model("raids_per_k ~ OtherWhite + Indian + Pakistani + Bangladeshi\
+ Chinese + OtherAsian + African + Caribbean + OtherBlack + Arab", df_scaletrim)
fitted3 = model3.fit()
# az.plot_trace(fitted3)
summary3 = az.summary(fitted3)
summary3.to_csv('AmendedData\\bambi_summary_boxcox_trim.csv')

# Plot all 3
fig, axs = plt.subplots(3, 1, figsize=(8, 12))
for summ, t, ax in zip([summary, summary2, summary3],
                       ['Naive', 'Box-Cox', 'Box-Cox trimmed'],
                       axs):
    sns.pointplot('mean', summ.index, data=summ,
                  dodge=True, join=False, ci=None, ax=ax)
    # Get points, to use for error bars
    x_coords = []
    y_coords = []
    for point_pair in ax.collections:
        for x, y in point_pair.get_offsets():
            x_coords.append(x)
            y_coords.append(y)
    ax.errorbar(x_coords, y_coords, xerr=(1.96*summ['sd']).values, fmt=' ')
    ax.set_title(f'Regression estimates ({t})')
plt.tight_layout()
plt.savefig('Outputs\\ethn_regr_coefs_inc_trim.png')
