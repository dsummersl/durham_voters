from arcgis import utils
import pandas as pd
from tqdm import tqdm

lots = pd.read_csv('durham_parcels.csv')
lots = lots.set_index(['clean_address_y'], drop=False)

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
        # Found a new address that doesn't exist in our dataset, with no known
        # voter associated with it:
        new_addresses.append({
            'PARCEL_ID': row.PARCEL_ID,
            'voter_reg_num': '',
            'clean_full_street_x': row.clean_full_street_x,
            'clean_full_street_y': row.clean_full_street_y,
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
lots[[
    'PARCEL_ID', 'voter_reg_num',
    'address', 'lat', 'long',
    'first_name', 'middle_name', 'last_name', 'birth_age',
    'voter_status_desc', 'party_cd'
]].to_csv('durham_addresses.csv', index=False)
