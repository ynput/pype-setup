import pytest
from pypeapp.lib.config import update_dict


test_data_main = {
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


test_data = {
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

assert result == update_dict(test_data_main, test_data)
