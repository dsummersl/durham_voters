import pandas as pd
from .utils import create_address_fields, parse_address


def test_create_address_fields():
    sbe_data = pd.DataFrame({
        'mail_addr1': pd.Series([
            '3523 N ROXBORO ST # 3H',
            '111 E CHANNING AVE  ',
            '801  LORAINE AVE',
            '  707   EAST   HUDSON AVE',
            '53 MOXY HUDSON AVE #7F',
            '116� E EDGEWOOD DR',
            '3805 CHIMNEY RIDGE PL Unit 08',
            '10 GREEN ST #Apt10F',
        ])
    })
    create_address_fields(sbe_data, 'mail_addr1')
    assert list(sbe_data['clean_street_number']) == ['3523', '111', '801', '707', '53', '116', '3805', '10']
    assert list(sbe_data['clean_street_name']) == ['ROXBORO', 'CHANNING', 'LORAINE', 'HUDSON', 'MOXY HUDSON', 'EDGEWOOD', 'CHIMNEY RIDGE', 'GREEN']
    assert list(sbe_data['clean_street_directional']) == ['N', 'E', '', 'E', '', 'E', '', '']
    assert list(sbe_data['clean_street_type']) == ['ST', 'AVE', 'AVE', 'AVE', 'AVE', 'DR', 'PL', 'ST']
    assert list(sbe_data['clean_street_apartment']) == ['3H', '', '', '', '7F', '', '8', '10F']

    assert list(sbe_data['clean_address']) == [
        '3523 N ROXBORO ST #3H',
        '111 E CHANNING AVE',
        '801 LORAINE AVE',
        '707 E HUDSON AVE',
        '53 MOXY HUDSON AVE #7F',
        '116 E EDGEWOOD DR',
        '3805 CHIMNEY RIDGE PL #8',
        '10 GREEN ST #10F',
    ]

    assert list(sbe_data['clean_full_street']) == [
        'N ROXBORO ST',
        'E CHANNING AVE',
        'LORAINE AVE',
        'E HUDSON AVE',
        'MOXY HUDSON AVE',
        'E EDGEWOOD DR',
        'CHIMNEY RIDGE PL',
        'GREEN ST',
    ]


def test_parse_address():
    assert parse_address('3146 FAYETTEVILLE ST') == {
            'clean_street_number': '3146',
            'clean_street_name': 'FAYETTEVILLE',
            'clean_street_directional': '',
            'clean_street_type': 'ST',
            'clean_street_apartment': '',
            'clean_address': '3146 FAYETTEVILLE ST'
        }

    assert parse_address('3146 SW FAYETTEVILLE ST 1A') == {
            'clean_street_number': '3146',
            'clean_street_name': 'FAYETTEVILLE',
            'clean_street_directional': 'SW',
            'clean_street_type': 'ST',
            'clean_street_apartment': '1A',
            'clean_address': '3146 SW FAYETTEVILLE ST #1A'
        }

    assert parse_address('1008 KINGSWOOD DR F') == {
            'clean_street_number': '1008',
            'clean_street_name': 'KINGSWOOD',
            'clean_street_directional': '',
            'clean_street_type': 'DR',
            'clean_street_apartment': 'F',
            'clean_address': '1008 KINGSWOOD DR #F'
        }
