import pytest
from pypeapp.lib import config


source_data = {
    'A01': {
        'A01/B01': {
            'A01/B01/C01': 'A01/B01/C01/D01',
            'A01/B01/C02': 'A01/B01/C02/D01'
        },
        'A01/B02': {'A01/B02/C01': 'A01/B02/C01/D01'}
    },
    'A02': {
        'A02/B01': ['A02/B01/C01', 'A02/B01/C02']
    },
    'A03': 'A03/B01'
}


new_data = {
    'A01': {
        'A01/B01': {
            'A01/B01/C02': 'test_output_1'
        },
        'A01/B02': 'test_output_2'
    },
    'A02': {
        'A02/B01': ['test_output_3']
    }
}


result = {
    'A01': {
        'A01/B01': {
            'A01/B01/C01': 'A01/B01/C01/D01',
            'A01/B01/C02': 'test_output_1'
        },
        'A01/B02': 'test_output_2'
    },
    'A02': {
        'A02/B01': ['test_output_3']
    },
    'A03': 'A03/B01'
}


def test_update_dict():

    assert result == config.update_dict(source_data, new_data)
