# Fire Districts

The state of North Carolina publishes fire districts, stations, parcels, and parcel centroids
on their nconemap.gov site. This project seeks to analyze this data to provide further insight
into the fire districting approach in the Valdese area.

## Data Sources

The following sites provide data that should prove useful in this analysis:

- https://www.burkenc.org/2495/Data-Sets
- https://www.nconemap.gov/#directdatadownloads
	- [Fire Stations](https://www.nconemap.gov/datasets/6f4fe0c55b0d4cbb92877e461d698c29_0/about)
	- [Fire Districts](https://www.nconemap.gov/datasets/abc2d489a9484854b21ffb029eb45a98/explore)

In order to maintain a clean repository, all downloaded and generated data will be maintained
in the parent `data` folder one level up from this repository.

The Fire District geometries published by nconemap.gov must be repaired/fixed prior to using
the Python analysis scripts. We used QGIS `Vector > Geometry Tools > Fix Geometries` for this.

The property valuations published by nconemap.gov fall a little short of the budget valuations
published by [Burke County's 2025-26 Approved Budget][budget25_26],
but they are consistently lower across the fire districts.

## Requirements

Where possible and appropriate, Python 3 will be used for analysis. The following packages
are required and must be established in the run time env by the user:

- GDAL/osgeo
- geopy

## Historical Tax Rates

Historical data for county managed fire districts can be seen in the [Burke 2021 Revised Audit report][burkefdratehistory].

[budget25_26]: https://www.burkenc.org/DocumentCenter/View/4471/FY-2025-2026-Approved-Budget-PDF#page=6
[burkefdratehistory]: https://lgreports.nctreasurer.com/Reports/2021/County/Burke.pdf#page=111