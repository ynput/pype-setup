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
    # TODO: write test for formatting.py/_solve_optional
    pass


def test_slicing():
    # TODO: write test for formatting.py/_slicing()
    pass
