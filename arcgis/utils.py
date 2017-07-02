import os
import pickle
import re
import requests
from functools import wraps


def memoize(cache_file):
    """ File backed memoize function """
    def wrap(func):
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)
        else:
            cache = {}

        @wraps(func)
        def wrapped_fn(*args):
            if args not in cache:
                cache[args] = func(*args)
                # update the cache file
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache, f)
            return cache[args]
        return wrapped_fn
    return wrap


@memoize('data/lat_long.pkl')
def find_lat_long(address):
    """ Lookup an addresses latitude and longitude """
    pass


@memoize('data/clean_apartments.pkl')
def find_apartments(address):
    """ Given an address attempt to find apartments for the address.  """
    params = {'method': 'getAddressDropdown', 'returnFormat': 'json', 'term': address}
    print("lookup '{}'".format(address))
    r = requests.get('http://maps2.roktech.net/durhamnc_gomaps4/cfc/gomaps.cfc', params=params)
    return r.json()


def find_unique_apartments(address):
    """ Given an address, find all apartments for it, and return cleaned up
    addresses. """
    addresses = find_apartments(address)
    return list(map(lambda a: parse_address(a), set(addresses)))


def parse_address(address):
    """ Turn an address into a dictionary of address parts. """
    address = address.strip()
    matches = re.match(r'^([0-9]+)\S*(\s+(N|W|E|S|SW|SE|NW|NE))?\s+(.+)\s+([a-zA-Z]{2,})(\s+(\S+))?$', address)
    if not matches:
        print('NO Match: {}'.format(address))
        return {
            'clean_street_number': '',
            'clean_street_name': '',
            'clean_street_directional': '',
            'clean_street_type': '',
            'clean_street_apartment': '',
            'clean_address': address
        }
    if matches.group(7):
        clean_address = re.sub(r'\S+$', '#{}'.format(matches.group(7)), address)
    else:
        clean_address = address
    return {
        'clean_street_number': matches.group(1),
        'clean_street_name': matches.group(4),
        'clean_street_directional': matches.group(3) or '',
        'clean_street_type': matches.group(5),
        'clean_street_apartment': matches.group(7) or '',
        'clean_address': clean_address
    }


def create_address_fields(sbe_data, column):
    """ Cleanup SBE mail_addr1 field from sbe_data. """
    sbe_data['clean_street_number'] = sbe_data[column].str.replace(r'^\s*([0-9]+)\S*\s+.*$', r'\1')
    apartments = sbe_data[column].str.contains(r'\s+#').fillna(False)
    units = sbe_data[column].str.contains(r'\bunit ', flags=re.IGNORECASE).fillna(False)
    sbe_data['clean_street_name'] = ''
    sbe_data.loc[apartments, 'clean_street_name'] = sbe_data.loc[apartments, column].str.replace(r'^\s*[0-9]+\S*\s+(.+)\s+\S+\s+#.*$', r'\1')
    sbe_data.loc[~apartments, 'clean_street_name'] = sbe_data.loc[~apartments, column].str.replace(r'^\s*[0-9]+\S*\s+(.+)\s+\S+.*$', r'\1')
    sbe_data.loc[units, 'clean_street_name'] = sbe_data.loc[units, column].str.replace(r'^\s*[0-9]+\S*\s+(.+)\s+\S+\s+unit\s+.*$', r'\1', flags=re.IGNORECASE)
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^EAST\s+(\S+)$', r'E \1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^WEST\s+(\S+)$', r'W \1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^NORTH\s+(\S+)$', r'N \1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^SOUTH\s+(\S+)$', r'S \1')
    sbe_data['clean_street_directional'] = ''
    sbe_data['clean_street_directional'] = sbe_data['clean_street_name'].str.replace(r'^(N|S|W|E|NE|NW|SE|SW)? ?\S+.*$', r'\1')
    sbe_data['clean_street_name'] = sbe_data['clean_street_name'].str.replace(r'^(N|S|W|E|NE|NW|SE|SW) ', '')
    sbe_data['clean_street_type'] = ''
    sbe_data.loc[apartments, 'clean_street_type'] = sbe_data.loc[apartments, column].str.replace(r'^\s*[0-9]+\S*\s+.*\s+(\S+)\s+#.*$', r'\1')
    sbe_data.loc[~apartments, 'clean_street_type'] = sbe_data.loc[~apartments, column].str.replace(r'^\s*[0-9]+\S*\s+.*\s+(\S+).*$', r'\1')
    sbe_data.loc[units, 'clean_street_type'] = sbe_data.loc[units, column].str.replace(r'^\s*[0-9]+\S*\s+.+\s+(\S+)\s+unit\s+.*$', r'\1', flags=re.IGNORECASE)
    sbe_data['clean_street_apartment'] = ''
    sbe_data.loc[apartments, 'clean_street_apartment'] = sbe_data.loc[apartments, column].str.replace(r'^\s*[0-9]+\S*\s+.*\s+#\s*(.*)$', r'\1')
    sbe_data.loc[units, 'clean_street_apartment'] = sbe_data.loc[units, column].str.replace(r'^\s*[0-9]+\S*\s+.+\s+\S+\s+unit\s+(.*)$', r'\1', flags=re.IGNORECASE)
    sbe_data['clean_street_apartment'] = sbe_data['clean_street_apartment'].str.replace(r'^0', '')
    sbe_data['clean_street_apartment'] = sbe_data['clean_street_apartment'].str.replace(r'^APT', '', flags=re.IGNORECASE)
    sbe_data['clean_address'] = '' + sbe_data['clean_street_number']
    sbe_data['clean_address'] = sbe_data['clean_address'] + sbe_data['clean_street_directional'].str.replace(r'^(\S+)$', r' \1')
    sbe_data['clean_address'] = sbe_data['clean_address'] + ' ' + sbe_data['clean_street_name']
    sbe_data['clean_address'] = sbe_data['clean_address'] + ' ' + sbe_data['clean_street_type']
    sbe_data['clean_address'] = sbe_data['clean_address'] + sbe_data['clean_street_apartment'].str.replace(r'^(\S+)$', r' #\1')
    has_directional = sbe_data['clean_street_directional'].str.contains(r'^$').fillna(False)
    sbe_data['clean_full_street'] = ''
    sbe_data.loc[~has_directional, 'clean_full_street'] = sbe_data.loc[~has_directional, 'clean_street_directional'].str.replace(r'^(.*)$', r'\1 ')
    sbe_data['clean_full_street'] = sbe_data['clean_full_street'] + sbe_data['clean_street_name']
    sbe_data['clean_full_street'] = sbe_data['clean_full_street'] + ' ' + sbe_data['clean_street_type']
