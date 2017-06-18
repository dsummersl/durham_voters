from arcgis import utils
import pandas as pd
from tqdm import tqdm

lots = pd.read_csv('durham_parcels.csv')
# lots = pd.read_csv('head.csv')
lots = lots.set_index(['clean_address_y'], drop=False)

searched = []

for i, row in tqdm(lots.iterrows(), total=lots.shape[0]):
    address = row['clean_full_street_y']
    if isinstance(address, float):
        address = row['clean_full_street_x']
    if address in searched:
        continue
    searched.append(address)
    # Search for all apartments on the full street name (to minimize HTTP calls):
    apartments = utils.find_unique_apartments(address)
    if len(apartments) == 0:
        continue
    new_addresses = []
    for a in apartments:
        if a['clean_street_apartment'] == '':
            # Don't include the 'lot address' if there are apartments
            continue
        not_in_lots = a['clean_address'] not in lots.index
        if not not_in_lots:
            continue
        new_addresses.append([
            row.PARCEL_ID,
            '',  # row.voter_reg_num,
            row.clean_number_address,
            row.clean_full_street_x,
            row.clean_full_street_y,
            '',  # row.clean_address_x,
            a['clean_address'],
            row.lat,
            row.long,
            '',  # row.first_name,
            '',  # row.middle_name,
            '',  # row.last_name,
            '',  # row.birth_age,
            '',  # row.voter_status_desc,
            ''   # row.party_cd
        ])
    if len(new_addresses) > 0:
        lots = lots.append(new_addresses)
        print('{}: {} new addresses'.format(row['clean_number_address'], len(new_addresses)))

lots.to_csv('durham_addresses.csv', index=False)
# TODO if there is a clean_number_address with a lot/long, when adding new
# missing lots, use the lat/long from other parcels (if there is one).
