"""Test the MadDashHistogram class."""

from typing import List, Union

import pytest  # type: ignore
from mad_dash_histogram import MadDashHistogram


class TestMadDashHistogram:
    """Unit test the MadDashHistogram class."""

    @staticmethod
    def assert_values(histogram: MadDashHistogram, name: str, xmax: Union[int, float],
                      xmin: Union[int, float], overflow: int, underflow: int, nan_count: int,
                      bin_values: List[int]):
        """Assert each value is in the histogram."""
        assert histogram.name == name
        assert histogram.xmax == xmax
        assert histogram.xmin == xmin
        assert histogram.overflow == overflow
        assert histogram.underflow == underflow
        assert histogram.nan_count == nan_count
        assert histogram.bin_values == bin_values

    def test_10(self):
        """Test basic functionality."""
        name = 'test'
        xmax = 10
        xmin = 0
        overflow = 5
        underflow = 3
        nan_count = 12
        bin_values = [0, 2, 4, 5, 9, 8, 5]

        histogram = MadDashHistogram(name, xmax, xmin, overflow, underflow, nan_count, bin_values)
        TestMadDashHistogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                           nan_count, bin_values)

        history = [200, 500]
        histogram.history = history
        assert histogram.history == history

    def test_11(self):
        """Test alternative types."""
        name = 'test'
        xmax = 100.1
        xmin = 0.023
        overflow = 5
        underflow = 3
        nan_count = 12
        bin_values = [0, 2, 4.02, 5, 9.486, 8, 5]

        histogram = MadDashHistogram(name, xmax, xmin, overflow, underflow, nan_count, bin_values)
        TestMadDashHistogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                           nan_count, bin_values)

        history = [10.25, 300]
        histogram.history = history
        assert histogram.history == history

    def test_20(self):
        """Fail-test name attribute."""
        with pytest.raises(NameError):
            _ = MadDashHistogram('filelist', 0, 0, 0, 0, 0, [])

    def test_30(self):
        """Test from_dict() and to_dict()."""
        name = 'test'
        xmax = 100.1
        xmin = 0.023
        overflow = 5
        underflow = 3
        nan_count = 12
        bin_values = [0, 2, 4.02, 5, 9.486, 8, 5]
        history = [10.25, 300]
        extra_value = 'extra'
        dict_ = {
            'name': name,
            'xmax': xmax,
            'xmin': xmin,
            'overflow': overflow,
            'underflow': underflow,
            'nan_count': nan_count,
            'bin_values': bin_values,
            'history': history,
            'extra_value': extra_value
        }

        histogram = MadDashHistogram.from_dict(dict_)
        TestMadDashHistogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                           nan_count, bin_values)

        out_dict = histogram.to_dict()
        assert dict_ == out_dict
