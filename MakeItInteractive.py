# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 17:00:28 2019

@author: setat
"""

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import Search

# Create map, focus on London
ldn = folium.Map(location=[51.53, -0.11], tiles='cartodbpositron',
                   zoom_start=11, control_scale=True)  # London, baby

# =============================================================================
# .shp to JSON
# =============================================================================

data_shp = 'Data\TotalLondonPostcodesWithData.shp'

# Read Data
data = gpd.read_file(data_shp)

# Re-project to WGS84
data['geometry'] = data['geometry'].to_crs(epsg=4326)

# Update the CRS of the GeoDataFrame
data.crs = {'init' :'epsg:4326'}

# Make a selection (only data above 0 and below 1000)
data['PostDist'] = data['PostArea'] + data['DistNum']

# Select data
data = data[['DistID', 'PostDist', 'Locale', 'Count', 'geometry']]

# Save the file as geojson
jsontxt = data.to_json()

# Structure of JSON
"""{"id": "125", "type": "Feature",
    "properties": {"DistID": 2346, "PostDist": "SW6",
                   "Locale": "Fulham", "Count": 110.0},
    "geometry": {"type": "Polygon", "coordinates": [[[-0.22251212906295376,
"""

# =============================================================================
# Visualise with Folium
# =============================================================================

# Create Choropleth map with custom bins
count_bins = [1, 100, 300, 500, 1000, 1250]

chorototal = folium.Choropleth(
geo_data=jsontxt,
    name='Raids',
    data=data,
    columns=['PostDist', 'Count'],
    key_on='feature.properties.PostDist',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    bins=count_bins,
    highlight=True,
    legend_name='Number of raids'
).add_to(ldn)

# Add tooltips with area details
folium.GeoJsonTooltip(
        fields=['PostDist', 'Locale', 'Count'],
        aliases=['Postcode', 'Place', '# raids'],
        ).add_to(chorototal.geojson)

# Create additional layer for 'raids by population'
popn = pd.read_csv('Data\\LondonPop.csv', index_col='Postcode')
# Add in the missing district populations
missing_pop = pd.read_csv('RawData\\missingpop.csv', header=None)
missing_pop = missing_pop.dropna()
missing_pop.columns = ['id', 'Postcode', 'Residents']
missing_pop = missing_pop.set_index('Postcode')
missing_pop = missing_pop.drop('id', axis=1)
popn = pd.concat([popn,missing_pop])
popn = popn.join(data.set_index('PostDist')['Count'])
popn['Rate'] = (popn['Count'] / popn['Residents'])*1000
popn.to_csv('Data\\PopnRaidsRate.csv')

#popn_bins = list(popn['Rate'].quantile([0, 0.12, 0.25, 0.5, 0.75, 1]))
popn_bins = [0.1,2,4,6,8,10,20,70]

chororate = folium.Choropleth(
    geo_data=jsontxt,
    name='Raids_per_1000',
    data=popn.reset_index(),
    columns=['Postcode', 'Rate'],
    key_on='feature.properties.PostDist',
    fill_color='PuRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    bins=popn_bins,
    legend_name='Raids per 1000 people',
    show=False
).add_to(ldn)

folium.GeoJsonTooltip(
        fields=['PostDist', 'Locale'],
        labels=False
        ).add_to(chororate.geojson)

folium.LayerControl(collapsed=False).add_to(ldn)

districtsearch = Search(
    layer=chorototal,
    geom_type='Polygon',
    placeholder='Search for a postcode district',
    collapsed=False,
    search_label='PostDist',
    weight=3
).add_to(ldn)

# Save the output
outfp = r'choropleth.html'
ldn.save(outfp)