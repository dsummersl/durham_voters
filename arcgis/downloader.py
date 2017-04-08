import json
import os
import requests
import geopandas as gpd

def strip_features(data):
    for row in data['features']:
        for k,v in row['attributes'].items():
            if isinstance(v, str):
                row['attributes'][k] = v.strip()
    return data

def download_arcgis(url, filename):
    """ Download a full arcgis to filename.

    The arcgis server may have a limit to how many records you can download in
    one request. To avoid this exceededTransferLimit error, I batch the requests
    in chunks.
    """
    ids_request = requests.get("{}&returnIdsOnly=true".format(url))
    ids = ids_request.json()
    id_chunks = [ids['objectIds'][x:x+150] for x in range(0, len(ids['objectIds']), 150)]

    first_data = None
    for chunk in id_chunks:
        chunk_url = "{}&objectIds={}".format(url, ','.join(str(c) for c in chunk))
        data_request = requests.get(chunk_url)
        data = data_request.json()
        if first_data is None:
            first_data = strip_features(data)
        else:
            first_data['features'].extend(strip_features(data)['features'])

    with open(filename,'w') as outfile:
        json.dump(first_data, outfile)

def download_shp(url, name):
    """ Download GIS data from an arcgis URL, and convert it to geojson and
    tiger shapefile.

    This will create {name}.json (arcgis format), {name}.geojson and {name}.shp
    """
    download_arcgis(url, '{}.json'.format(name))
    data = gpd.GeoDataFrame.from_file('{}.json'.format(name))
    data.to_file('{}.geojson')
    data.to_file('{}.shp')
    return data
