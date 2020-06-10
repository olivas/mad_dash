"""Test the api.Histogram class."""

from typing import List, Union

import pytest  # type: ignore

# local imports
import maddash_api as api


class TestAPIHistogram:
    """Unit test the api.Histogram class."""

    @staticmethod
    def assert_values(histogram: api.Histogram, name: str, xmax: Union[int, float],
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

        histogram = api.Histogram(name, xmax, xmin, overflow, underflow, nan_count, bin_values)
        TestAPIHistogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
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

        histogram = api.Histogram(name, xmax, xmin, overflow, underflow, nan_count, bin_values)
        TestAPIHistogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                       nan_count, bin_values)

        history = [10.25, 300]
        histogram.history = history
        assert histogram.history == history

    def test_20(self):
        """Fail-test name attribute."""
        with pytest.raises(NameError):
            _ = api.Histogram('filelist', 0, 0, 0, 0, 0, [])

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

        histogram = api.Histogram.from_dict(dict_)
        TestAPIHistogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                       nan_count, bin_values)

        out_dict = histogram.to_dict()
        assert dict_ == out_dict

    def test_31(self):
        """Test to_dict() with 'exclude' keys."""
        extra = 5
        addl = ['a']
        keeps = 2.0

        histo = api.Histogram('test', 0, 0, 0, 0, 0, [])
        histo.extra = extra
        histo.addl = addl
        histo.keeps = keeps
        dict_ = histo.to_dict(exclude=['extra', 'addl'])

        assert histo.extra == extra
        assert 'extra' not in dict_

        assert histo.addl == addl
        assert 'addl' not in dict_

        assert dict_['keeps'] == keeps == histo.keeps
