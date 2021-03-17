# Immigration raids in London

This repo contains the data behind the https://antiraids.github.io/ FOI investigation.

### Data

`file_1.csv` contains X and Y broken down by Z.

Column | Description
-------|---------------
`column_1` |	Blah 1
`column_2` |	Blah 2

### Methodology

~~_**Data source**: immigration raid data from FOIs submitted by Haringey Anti-Raids and others in the anti-raids network; population counts from 2011 census data._~~

**Timespan:** the FOI data runs from 2014 to 2019 inclusive.

**Tools used:**

- Python for the core analysis
- Folium and Geopandas packages to visualise the data in a choropleth map, weighed by number of immigration raids since 2014, and also optionally by immigration raids per 1,000 residents.

Hat tip to [this AutoGIS walk-through](https://automating-gis-processes.github.io/2016/Lesson5-interactive-map-folium.html), and [Folium's clear documentation](https://python-visualization.github.io/folium/quickstart.html#Choropleth-maps).

By "London", we mean the London postal district i.e. any postcode with postcode area N, NW, SW, SE, W, WC, E or EC.