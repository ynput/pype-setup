import pytest
from pypeapp import formatting


def test_dict_to_obj():
    test = {
        'data_A': {
            'A': '1',
            'B': '2'
        },
        'data_B': {
            'C': '3',
            'D': '4'
        }
    }

    dotstr = formatting._Dict_to_obj_with_range(test)
    assert dotstr['data_A'].A == '1'
    assert dotstr['data_A'].B == '2'
    assert dotstr['data_B'].C == '3'
    assert dotstr['data_B'].D == '4'
    pass


def test_dict_to_obj_levels():
    test = {
        'data_A': {
            'A': [0, 1, 2],
            'B': {'data': 'test'}
        },
        'data_B': {
            'C': (0, 1, 2),
            'D': 1,
            'E': True,
            'F': None
        }
    }
    dotstr = formatting._Dict_to_obj_with_range(test)
    assert dotstr['data_A'].A[0] == 0
    assert dotstr['data_A'].A[1] == 1
    assert dotstr['data_A'].A[2] == 2
    assert dotstr['data_A'].B.data == 'test'
    assert dotstr['data_B'].C[0] == 0
    assert dotstr['data_B'].C[1] == 1
    assert dotstr['data_B'].C[2] == 2
    assert dotstr['data_B'].D == 1
    assert dotstr['data_B'].E is True
    assert dotstr['data_B'].F is None
    pass


def test_solve_optional():
    template = "{data_A}<_{data_B}>"
    test_data_1 = {
        'data_A': "iamrequiredKey",
        'data_B': "iamoptionalkey"
    }
    test_data_2 = {
        'data_A': "iamrequiredKey"
    }
    formatted_with_optional = formatting._solve_optional(template, test_data_1)
    formatted_no_optional = formatting._solve_optional(template, test_data_2)

    assert formatted_with_optional == "iamrequiredKey_iamoptionalkey"
    assert formatted_no_optional == "iamrequiredKey"


def test_slicing():

    # TODO: improve this test
    # this should probably be able to handle two keys with slicing within
    # a single template. I'm not sure we actually need this function though

    template = "{key1[0:1]}"

    sliced_template, pairs = formatting._slicing(template)

    assert sliced_template == "{key1}"
    assert pairs == [('key1', [0, 1])]


def test_format():
    template = "{dictKey[A][0]}_{dictKey[B][data]}<_{intKey}>_{key3}<_{missingKey}>"
    test = {
        'dictKey': {
            'A': ["first", 25, 80],
            'B': {'data': 'test'}
        },
        'intKey': 10,
        'key3': "stringKey"
    }
    formatted = formatting.format(template, test)

    assert formatted == "first_test_10_stringKey"
