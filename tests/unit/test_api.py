"""Test the api.py."""

from typing import List

import pytest  # type: ignore

# local imports
from api import I3Histogram, Num


class TestI3Histogram:
    """Unit test the I3Histogram class."""

    # pylint: disable=R0913
    @staticmethod
    def assert_values(histogram: I3Histogram, name: str, xmax: Num, xmin: Num, overflow: int,
                      underflow: int, nan_count: int, bin_values: List[Num]) -> None:
        """Assert each value is in the histogram."""
        assert histogram.name == name
        assert histogram.xmax == xmax
        assert histogram.xmin == xmin
        assert histogram.overflow == overflow
        assert histogram.underflow == underflow
        assert histogram.nan_count == nan_count
        assert histogram.bin_values == bin_values

    @staticmethod
    def test_10() -> None:
        """Test basic functionality."""
        name = 'test'
        xmax = 10
        xmin = 0
        overflow = 5
        underflow = 3
        nan_count = 12
        bin_values = [0, 2, 4, 5, 9, 8, 5]  # type: List[Num]

        histogram = I3Histogram(name, xmax, xmin, overflow, underflow, nan_count, bin_values)
        TestI3Histogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                      nan_count, bin_values)

        history = [200, 500]  # type: List[Num]
        histogram.history = history
        assert histogram.history == history

    @staticmethod
    def test_11() -> None:
        """Test alternative types."""
        name = 'test'
        xmax = 100.1
        xmin = 0.023
        overflow = 5
        underflow = 3
        nan_count = 12
        bin_values = [0, 2, 4.02, 5, 9.486, 8, 5]  # type: List[Num]

        histogram = I3Histogram(name, xmax, xmin, overflow, underflow, nan_count, bin_values)
        TestI3Histogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                      nan_count, bin_values)

        history = [10.25, 300]
        histogram.history = history
        assert histogram.history == history

    @staticmethod
    def test_20() -> None:
        """Fail-test name attribute."""
        with pytest.raises(NameError):
            _ = I3Histogram('filelist', 0, 0, 0, 0, 0, [])

    @staticmethod
    def test_30() -> None:
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

        histogram = I3Histogram.from_dict(dict_)
        TestI3Histogram.assert_values(histogram, name, xmax, xmin, overflow, underflow,
                                      nan_count, bin_values)

        out_dict = histogram.to_dict()
        assert dict_ == out_dict

    @staticmethod
    def test_31() -> None:
        """Test to_dict().

        Test with 'exclude' keys and dynamically-added attributes.
        """
        extra = 5
        addl = ['a']
        keeps = 2.0

        histo = I3Histogram('test', 0, 0, 0, 0, 0, [])
        histo.extra = extra  # type: ignore
        histo.addl = addl  # type: ignore
        histo.keeps = keeps  # type: ignore
        dict_ = histo.to_dict(exclude=['extra', 'addl'])

        assert histo.extra == extra  # type: ignore
        assert 'extra' not in dict_

        assert histo.addl == addl  # type: ignore
        assert 'addl' not in dict_

        assert 'keeps' in dict_
        assert dict_['keeps'] == keeps == histo.keeps  # type: ignore
