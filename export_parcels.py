from arcgis import downloader, utils
import geopandas as gpd
import pandas as pd

print('Load shape data')
durham = gpd.GeoDataFrame.from_file("data/durham.shp")

print('Load lots')
lots = {}
for precinct in durham['PREC_ID'].unique():
    bounds = durham[durham.PREC_ID == precinct].bounds
    all_lots_url_template = "http://gisweb2.durhamnc.gov/arcgis/rest/services/PublicWorks/PublicWorks/MapServer/89/query?f=json&geometry={},{},{},{}&returnGeometry=true&outFields=*&outSR=4326&inSR=4326"
    lots[precinct] = downloader.get_shp(all_lots_url_template, 'data/all_lots-{}'.format(precinct), bounds)

print('Cleanup lots')
all_lots = pd.concat(lots.values())
# b/c of rectangular arcgis regions and precincts are within those regions,
# there will be some lots listed twice. Delete dups:
all_lots = all_lots.drop_duplicates(['PARCEL_ID'])
print('lots = {}'.format(len(all_lots)))

all_lots['lat_long'] = all_lots.centroid
all_lots['lat'] = all_lots['lat_long'].map(lambda ll: ll.y)
all_lots['long'] = all_lots['lat_long'].map(lambda ll: ll.x)
utils.create_address_fields(all_lots, 'SITE_ADDRE')

print('Load voters')
voters = pd.read_csv('data/ncvoter32.txt', sep=None)
voters_in_county = voters[voters.county_desc == "DURHAM"]
# cut out 'removed' voters
voters_in_county = voters[voters.voter_status_desc != "REMOVED"]
utils.create_address_fields(voters_in_county, 'res_street_address')

print('Create common address column')
voters_in_county['clean_number_address'] = voters_in_county['clean_street_number'] + ' ' + voters_in_county['clean_full_street']
all_lots['clean_number_address'] = all_lots['clean_street_number'] + ' ' + all_lots['clean_full_street']
# address without street directional or type at end:
voters_in_county['clean_number_street'] = voters_in_county['clean_street_number'] + ' ' + voters_in_county['clean_street_name']
all_lots['clean_number_street'] = all_lots['clean_street_number'] + ' ' + all_lots['clean_street_name']

print('Merge & Gen Stats')
by_address = all_lots.merge(voters_in_county, on='clean_number_address', how='inner')

remaining_lots = all_lots[~all_lots.PARCEL_ID.isin(by_address.PARCEL_ID)]
remaining_voters = voters_in_county[~voters_in_county.voter_reg_num.isin(by_address.voter_reg_num)]
by_street = remaining_lots.merge(remaining_voters, on='clean_number_street', how='outer')

merged_lots = pd.concat([by_address, by_street])

group_cols = [
    'PARCEL_ID', 'LANDUSE_DE', 'clean_number_address',
    'clean_full_street_x', 'clean_full_street_y',
    'clean_address_x', 'clean_address_y']
grouped = merged_lots[group_cols + [
    'lat', 'long', 'birth_age', 'voter_status_desc', 'party_cd'
]]
grouped[group_cols] = grouped[group_cols].fillna('')
grouped[['lat', 'long']] = grouped[['lat', 'long']].fillna(0)
grouped = grouped.groupby(group_cols + ['lat', 'long'])
aggregations = {
    'birth_age': {
        'avg_age': 'mean'
    },
    'voter_status_desc': {
        'num_voters': 'count',
        'percent_active_voters': lambda x: len(x[x == 'ACTIVE']) / len(x)
    },
    'party_cd': {
        'percent_democrat': lambda x: len(x[x == 'DEM']) / len(x)
    }
}
grouped = grouped.agg(aggregations)

# Drop the first index which is the birth_age, etc that were aggregated into the
# second index:
grouped.columns = grouped.columns.droplevel()
print('exported addresses: {}'.format(len(grouped)))
# print('exported w/c latlng: {}'.format(len(grouped[grouped[grouped.lat == '']])))

print('Save')

# Include both lot and voter address - b/c voters not matched to a lot will have
# an address that may be useful for finding apartments.
grouped.to_csv('data/durham_parcels.csv')
