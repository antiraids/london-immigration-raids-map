# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 17:00:28 2019

@author: setat
"""

import folium
import geopandas as gpd
import pandas as pd

# =============================================================================
# Trial using Folium to make an HTML map
# =============================================================================

ldn = folium.Map(location=[51.50, -0.11], tiles='cartodbpositron',
                   zoom_start=11, control_scale=True)  # London, baby

outfp = "base_map.html"
ldn.save(outfp)  # ooh, successful

# =============================================================================
# .shp to JSON
# =============================================================================

pd_shp = 'RawData\GB_Postcodes\PostalDistrict.shp'
data_shp = 'AmendedData\TotalLondonPostcodesWithData.shp'

# Read Data
pd_df = gpd.read_file(pd_shp)
data = gpd.read_file(data_shp)
#data = gpd.read_file(fp)
#ad = gpd.read_file(addr_fp)

# Re-project to WGS84
pd_df['geometry'] = pd_df['geometry'].to_crs(epsg=4326)
data['geometry'] = data['geometry'].to_crs(epsg=4326)
#data['geometry'] = data['geometry'].to_crs(epsg=4326)
#ad['geometry'] = ad['geometry'].to_crs(epsg=4326)

# Update the CRS of the GeoDataFrame
pd_df.crs = {'init' :'epsg:4326'}
data.crs = {'init' :'epsg:4326'}
#data.crs = from_epsg(4326)
#ad.crs = from_epsg(4326)

# Make a selection (only data above 0 and below 1000)
pd_df = pd_df[pd_df['PostDist'].str.contains(
        '^(EC?|S[EW]|NW?|WC?)\d', regex=True)]
data['PostDist'] = data['PostArea'] + data['DistNum']
#data = data.ix[(data['ASUKKAITA'] > 0) & (data['ASUKKAITA'] <= 1000)]

# Create a Geo-id which is needed by the Folium (it needs to have a unique identifier for each row)
#data['geoid'] = data.index.astype(str)
#ad['geoid'] = ad.index.astype(str)

# Select data
pd_df = pd_df[['DistID', 'PostDist', 'Sprawl', 'geometry']]
data = data[['DistID', 'PostDist', 'Locale', 'Count', 'geometry']]
#data = data[['geoid', 'ASUKKAITA', 'geometry']]

# Save the file as geojson
jsontxt = data.to_json()
#jsontxt = data.to_json()


# =============================================================================
# Visualise with Folium
# =============================================================================

# Create a Clustered map where points are clustered
#marker_cluster = folium.MarkerCluster().add_to(ldn)

# Create Choropleth map where the colors are coming from a column "ASUKKAITA".
# Notice: 'geoid' column that we created earlier needs to be assigned always as the first column
# with threshold_scale we can adjust the class intervals for the values
#ldn.choropleth(geo_str=jsontxt, data=pd_df, columns=['DistID', 'ASUKKAITA'],
#               key_on="feature.id", fill_color='YlOrRd', fill_opacity=0.9,
#               line_opacity=0.2, line_color='white', line_weight=0,
#               threshold_scale=[100, 250, 500, 1000, 2000],
#               legend_name='Population in Helsinki', highlight=False,
#               smooth_factor=1.0)

#bins = list(data['Count'].quantile([0, 0.12, 0.25, 0.5, 0.75, 1]))
count_bins = [1, 50, 100, 500, 1000, 1250]

folium.Choropleth(
    geo_data=jsontxt,
    name='Raids',
    data=data,
    columns=['PostDist', 'Count'],
    key_on='feature.properties.PostDist',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    bins=count_bins,
    legend_name='Raids 2014-2019'
).add_to(ldn)

"""{"id": "125", "type": "Feature",
    "properties": {"DistID": 2346, "PostDist": "SW6",
                   "Locale": "Fulham", "Count": 110.0},
    "geometry": {"type": "Polygon", "coordinates": [[[-0.22251212906295376,
"""

popn = pd.read_csv('AmendedData\\LondonPop.csv', index_col='Postcode')
popn = popn.join(data.set_index('PostDist')['Count'])
popn['Rate'] = (popn['Count'] / popn['Residents'])*1000

popn_bins = list(popn['Rate'].quantile([0, 0.12, 0.25, 0.5, 0.75, 1]))

folium.Choropleth(
    geo_data=jsontxt,
    name='Raids_per_1000',
    data=popn.reset_index(),
    columns=['Postcode', 'Rate'],
    key_on='feature.properties.PostDist',
    fill_color='PuRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    bins=popn_bins,
    legend_name='Raids per 1000 people, 2014-2019'
).add_to(ldn)

# Create Address points on top of the map
#for idx, row in ad.iterrows():
#    # Get lat and lon of points
#    lon = row['geometry'].x
#    lat = row['geometry'].y
#
#    # Get address information
#    address = row['address']
#    # Add marker to the map
#    folium.RegularPolygonMarker(location=[lat, lon], popup=address, fill_color='#2b8cbe', number_of_sides=6, radius=8).add_to(marker_cluster)

folium.LayerControl().add_to(ldn)

# Save the output
outfp = r'choropleth.html'
ldn.save(outfp)