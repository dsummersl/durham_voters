def create_address_fields(sbe_data, column):
    """ Cleanup SBE mail_addr1 field from sbe_data. """
    sbe_data['clean_street_number'] = sbe_data[column].str.replace(r'^([0-9]+) .*$', r'\1')
    apartments = sbe_data[column].str.contains(' # ').fillna(False)
    sbe_data['clean_street_name'] = ''
    sbe_data.loc[apartments, 'clean_street_name'] = sbe_data.loc[apartments, column].str.replace(r'^[0-9]+ (.+) \S+ # .*$', r'\1')
    sbe_data.loc[~apartments, 'clean_street_name'] = sbe_data.loc[~apartments, column].str.replace(r'^[0-9]+ (.+) \S+$', r'\1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^EAST (\S+)$', r'E \1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^WEST (\S+)$', r'W \1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^NORTH (\S+)$', r'N \1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^SOUTH (\S+)$', r'S \1')
    sbe_data['clean_street_directional'] = ''
    sbe_data['clean_street_directional'] = sbe_data['clean_street_name'].str.replace(r'^(N|S|W|E|NE|NW|SE|SW)? ?\S+.*$', r'\1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^(N|S|W|E|NE|NW|SE|SW) ', '')
    sbe_data['clean_street_type'] = ''
    sbe_data.loc[apartments, 'clean_street_type'] = sbe_data.loc[apartments, column].str.replace(r'^[0-9]+ .* (\S+) # .*$', r'\1')
    sbe_data.loc[~apartments, 'clean_street_type'] = sbe_data.loc[~apartments, column].str.replace(r'^[0-9]+ .* (\S+)$', r'\1')
    sbe_data['clean_street_apartment'] = ''
    sbe_data.loc[apartments, 'clean_street_apartment'] = sbe_data.loc[apartments, column].str.replace(r'^[0-9]+ .* # (.*)$', r'\1')
