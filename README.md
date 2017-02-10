Building
========

This app is intended to be deployed as a static app (no backend).

To build:

    npm run build

To run in debug mode:

    npm run watch

Rebuild shapefiles:

    rm Precincts-simplified*
    ./node_modules/.bin/mapshaper Precincts.shp -simplify 15% -o Precincts-simplified.shp
    rm src/Precincts.geojson
    ogr2ogr -f "GeoJSON" -t_srs crs:84 src/Precincts.geojson Precincts-simplified.shp
    ./node_modules/topojson-server/bin/geo2topo src/Precincts.geojson > src/Precincts.topojson
