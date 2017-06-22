from arcgis import utils
import pandas as pd
from tqdm import tqdm

lots = pd.read_csv('durham_parcels.csv')
lots = lots.set_index(['clean_address_y'], drop=False)
lots_by_number_address = lots.set_index(['clean_number_address'], drop=False)

searched = []
new_addresses = []

for i, row in tqdm(lots.iterrows(), total=lots.shape[0]):
    address = row['clean_full_street_y']
    if isinstance(address, float):
        address = row['clean_full_street_x']
    # Have we already searched this streed for addresses/apartments?
    if address in searched:
        continue
    searched.append(address)
    # Search for all addresses/apartments on the street to minimize HTTP calls:
    apartments = utils.find_unique_apartments(address)
    if len(apartments) == 0:
        continue
    for a in apartments:
        if a['clean_street_apartment'] == '':
            # Don't include the 'lot address' if it is not an apartment
            continue
        in_lots = a['clean_address'] in lots.index
        # Don't add the address if it already exists in our dataset:
        if in_lots:
            continue

        # This parcel id is often not correct b/c we do a bulk HTTP request
        # on the first parcel on a block. We need to add clean_number_address,
        # and add it as an index so that we can search for the matching street
        # and address number - if there is a match, use that. Otherwise nothing.
        number_address = a['clean_street_number'] + ' ' + a['clean_street_name'] + ' ' + a['clean_street_type']
        if len(a['clean_street_directional']) > 0:
            number_address = a['clean_street_number'] + ' ' + a['clean_street_directional'] + ' ' + a['clean_street_name'] + ' ' + a['clean_street_type']
        parcel_id = 0
        if number_address in lots_by_number_address.index:
            match = lots_by_number_address.loc[[number_address]]
            parcel_id = match.iloc[0].PARCEL_ID

        # Found a new address that doesn't exist in our dataset, with no known
        # voter associated with it:
        new_addresses.append({
            'PARCEL_ID': parcel_id,
            'voter_reg_num': '',
            'clean_full_street_x': row.clean_full_street_x,
            'clean_full_street_y': row.clean_full_street_y,
            'precinct_desc': row.precinct_desc,
            'clean_address_x': '',
            'clean_address_y': a['clean_address'],
            'lat': row.lat,
            'long': row.long,
            'first_name': '',
            'middle_name': '',
            'last_name': '',
            'birth_age': '',
            'voter_status_desc': '',
            'party_cd': ''
        })

if len(new_addresses) > 0:
    lots = lots.append(new_addresses, ignore_index=True)
    # print('{}: {} new addresses'.format(address, len(new_addresses)))

lots.PARCEL_ID = lots.PARCEL_ID.fillna(0).astype(int)
lots.voter_reg_num = pd.to_numeric(lots.voter_reg_num).fillna(0).astype(int)
lots = lots.fillna('')
no_lot_address = lots['clean_address_x'].str.contains(r'^$').fillna(False)
lots['address'] = '' + lots['clean_address_x']
lots.loc[no_lot_address, 'address'] = '' + lots.loc[no_lot_address, 'clean_address_y']

lots['precinct'] = lots['precinct_desc']

lots[[
    'PARCEL_ID', 'voter_reg_num', 'precinct',
    'address', 'lat', 'long',
    'first_name', 'middle_name', 'last_name', 'birth_age',
    'voter_status_desc', 'party_cd'
]].to_csv('durham_addresses.csv', index=False)
