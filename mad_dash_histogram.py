"""Histogram object for Mad Dash."""

import copy
from typing import Dict, List, Tuple, Union


class MadDashHistogram:
    """A representation of a histogram for Mad-Dash related purposes."""

    def __init__(self, name: str, xmax: Union[int, float], xmin: Union[int, float],
                 overflow: int, underflow: int, nan_count: int, bin_values: List[int]):
        types = {}  # type: Dict[str, Union[type, Tuple[type, ...]]]

        if name == 'filelist':
            raise NameError("histogram cannot be named 'filelist'")

        self.name = name  # type: str
        types['name'] = str

        self.xmax = xmax  # type:  Union[int, float]
        types['xmax'] = (int, float)

        self.xmin = xmin  # type: Union[int, float]
        types['xmin'] = (int, float)

        self.overflow = overflow  # type: int
        types['overflow'] = int

        self.underflow = underflow  # type: int
        types['underflow'] = int

        self.nan_count = nan_count  # type: int
        types['nan_count'] = int

        self.bin_values = bin_values  # type: List[int]
        types['bin_values'] = list

        # check types
        for attr_name, type_ in types.items():
            attr_value = self.__getattribute__(attr_name)
            if not isinstance(attr_value, type_):
                raise TypeError(f"Attribute should be {type_} not {type(attr_value)}")

        self.history = []  # type: List[Union[int, float]]

    @staticmethod
    def from_dict(dict_: dict) -> 'MadDashHistogram':  # https://github.com/python/typing/issues/58
        """Create a MadDashHistogram instance from a dict. Factory method.

        `dict_` must have correctly typed items and cannot have extra keys/fields.

        Arguments:
            dict_ -- the dictionary to be morphed

        Raises a {NameError} if there name field is illegal
        Raises a {AttributeError} if there's any extra keys (fields)
        Raises a {TypeError} if there's any mistyped items (attributes)
        """
        try:
            mdh = MadDashHistogram(dict_['name'],
                                   dict_['xmax'],
                                   dict_['xmin'],
                                   dict_['overflow'],
                                   dict_['underflow'],
                                   dict_['nan_count'],
                                   dict_['bin_values'])
        except KeyError as e:
            raise AttributeError(f"histogram has missing field {str(e)}")

        # add extra items
        mandatory_keys = ['name', 'xmax', 'xmin', 'overflow',
                          'underflow', 'nan_count', 'bin_values']
        for attr_name, attr_value in dict_.items():
            if attr_name not in mandatory_keys:
                mdh.__setattr__(attr_name, attr_value)

        return mdh

    def to_dict(self, exclude: List[str] = None) -> dict:
        """Return attributes as dictionary."""
        dict_ = copy.deepcopy(self.__dict__)

        # remove keys in `exclude`
        if exclude:
            for k in exclude:
                if k in dict_:
                    del dict_[k]

        return dict_
