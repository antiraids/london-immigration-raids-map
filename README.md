# Immigration raids in London

This repo contains the data behind the https://antiraids.github.io/ FOI investigation.

### How to used

1. `LondonRaids.py`: munge the FOI data into a useable format
2. `MakeItInteractive.py`: making the interactive choropleth
3. `ByEthnicity.py`: munging the ethnicity data
4. `Trends.py`: visualise, calculate trends
5. `TellingTheStory.ipynb`: making static plots for the site, along with the narrative of the analysis
6. `interactive_line.ipynb`: making interactive line plots of raids per area per year, for the site

### Data sources

Data file | Source | Used in
----------|--------|--------
`AmendedData\\LondonRaidsByYear.csv` | `LondonRaids.py` |  `TellingTheStory.ipynb`
`AmendedData\\TotalLondonRaidsByYear.csv` | `LondonRaids.py` |  `TellingTheStory.ipynb`, `Trends.py`
`AmendedData\\PopnRaidsRate.csv` | `MakeItInteractive.py` | `TellingTheStory.ipynb`
`AmendedData\\PostcodeEthnicityRates_toplevel.csv` | `ByEthnicity.py` | `TellingTheStory.ipynb`
`AmendedData\\PostcodeEthnicityRates_keylines.csv` | `ByEthnicity.py` | `TellingTheStory.ipynb`
`AmendedData\\RaidTrends.csv` | `Trends.py` | `TellingTheStory.ipynb`
`AmendedData\\TotalLondonPostcodesWithData.shp` | `LondonRaids.py` | `MakeItInteractive.py`
`AmendedData\\LondonPop.csv` | `LondonRaids.py` | `MakeItInteractive.py`
`RawData\\missingpop.csv` | "Street Check" e.g. for [EC4R](https://www.streetcheck.co.uk/postcodedistrict/ec4r) | `MakeItInteractive.py`
`RawData\\KS201EW_Postcode district_Ethnic group.csv` | [Nomis](https://www.nomisweb.co.uk/census/2011/ks201ew) | `ByEthnicity.py`
`RawData\55886 xxx Appendix A.xlsx` | Home Office FOI | `LondonRaids.py`
`RawData\57252 xxx Appendix A.xlsx` | Home Office FOI | `LondonRaids.py`
`RawData\56323 xxx Annex.xlsx` | Home Office FOI | `LondonRaids.py`
`RawData\56325 xxx Annex.xlsx` | Home Office FOI | `LondonRaids.py`
`RawData\\57894 PDF scrape_2019RaidsENW.txt` | Home Office FOI | `LondonRaids.py`
`PostalDistrict.shp`\* | From [University of Edinburgh](https://doi.org/10.7488/ds/1947), via [StackExchange](https://gis.stackexchange.com/questions/32321/seeking-postcode-shapefiles-for-uk) | `LondonRaids.py`
`RawData\PostDistNames.csv` | [Wikipedia](https://en.wikipedia.org/w/index.php?title=London_postal_district&oldid=917085462) | `LondonRaids.py`, to assign names to postcode areas
`RawData\ECPostDistNames.csv` | [Wikipedia](https://en.wikipedia.org/wiki/EC_postcode_area) | `LondonRaids.py`, to assign names to postcode areas
`RawData\Nomis KS101EW usual resident population London.csv` | [Nomis](http://www.nomisweb.co.uk/census/2011/ks101ew) | `LondonRaids.py`

\* not included in this repo for size reasons (as it is 85 MB)

### Notes

**Timespan:** the FOI data runs from 2014 to 2019 inclusive.

**Tools used:**

- Straight-up Python for the data munging and basic analysis
- Folium and Geopandas packages to visualise the data in a choropleth map, weighed by number of immigration raids since 2014, and also optionally by immigration raids per 1,000 residents.

Hat tips to:

- [this AutoGIS walk-through](https://automating-gis-processes.github.io/2016/Lesson5-interactive-map-folium.html)
- [Folium's clear documentation](https://python-visualization.github.io/folium/quickstart.html#Choropleth-maps)
- [this Towards Data Science walk-through](https://towardsdatascience.com/lets-make-a-map-using-geopandas-pandas-and-matplotlib-to-make-a-chloropleth-map-dddc31c1983d)

**Notes**:

- By "London", we mean the "London postal district" i.e. any postcode with postcode area N, NW, SW, SE, W, WC, E or EC.
- For a lot of the preparation time, the assumption was that "postcode district" was the correct term for what is actually technically the "outward code" -- so there are a lot of references to "district" and "postdist" in the code.