Overview
========

This is a set of iPython notebooks that analyze voting data in Durham, NC.

 * [County Analysis](./county-visualization.ipynb)
 * [Precinct Analysis](./precinct-visualization.ipynb)

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
