Overview
========

This is a set of iPython notebooks and python scripts that analyze voting data
in Durham County, NC.

Notebooks that show summaries of registered voters:

 * [County Analysis](./county-visualization.ipynb)
 * [Precinct Analysis](./precinct-visualization.ipynb)

Notebooks that show summaries of parcel and addresses:

 * [Precinct Apartments](./precinct-apartments.ipynb)

Setup
=====

1. Install GDAL (ogr2ogr utilities). On OSX this is as easy `brew install gdal`.
2. The `rtree` on OSX needs needs another library: `brew install spatialindex`.
3. Install a virtual environment and dependencies:

```bash

mkvirtualenv nc_election -p `which python3`
pip install -r requirements.txt
```

4. Run the notebook: `jupyter notebook`

Testing
=======

I'm slowly building a python library to clean up voter data.

```
pytest arcgis
```

Generating Data
===============

The `data/durham_addresses.csv.gz` is generated by combining addresses the
Durham County GIS database of parcels, and the NCSBE voter logs. Together these
data sources are then run against a Durham County API that identifies apartment
numbers for an address, which produces a comprehensive list of all addresses
(including apartments) in Durham County.

Since generating the dataset takes a couple hours, I've checked the latest
version of this CSV into the repository.

If you need to regenerate this dataset use the following instructions:

```
python export_parcels.py
python find_apartments.py
```
