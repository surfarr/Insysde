import pytest

from kadane import max_subarray, max_profit_window


def test_classic_example():
    r = max_subarray([-2, 1, -3, 7, -1, 2, 1, -5, 4])
    assert r == {"start": 3, "end": 6, "best_sum": 9}


def test_all_negatives_returns_largest_single():
    assert max_subarray([-5, -2, -8]) == {"start": 1, "end": 1, "best_sum": -2}


def test_single_element():
    assert max_subarray([4]) == {"start": 0, "end": 0, "best_sum": 4}


def test_all_positives_whole_list():
    assert max_subarray([1, 2, 3]) == {"start": 0, "end": 2, "best_sum": 6}


def test_empty_raises():
    with pytest.raises(ValueError):
        max_subarray([])


def test_tie_returns_earliest_window():
    # [3] and [3] tie; the earlier window is returned.
    assert max_subarray([3, -5, 3]) == {"start": 0, "end": 0, "best_sum": 3}


def test_profit_window_wrapper():
    assert max_profit_window([-2, 1, -3, 7, -1, 2, 1, -5, 4])["best_sum"] == 9
