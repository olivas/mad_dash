"""API for Mad-Dash-wide usages."""

import copy
import time
import typing
from typing import Any, Dict, Iterator, List, Optional, Tuple, TypedDict, Union

# types
Num = Union[int, float]


# types
class MongoHistogram(TypedDict):
    """Dict representation of a histogram for db, serialization, and typing."""

    name: str
    xmax: Num
    xmin: Num
    overflow: int
    underflow: int
    nan_count: int
    bin_values: List[Num]
    history: List[Num]


# types
FilelistList = List[str]
_FilelistDict = Dict[str, Union[Any, FilelistList]]
MongoCollection = Dict[str, Union[_FilelistDict, MongoHistogram]]


def yield_mongo_histograms(collection: MongoCollection) -> Iterator[MongoHistogram]:
    """Yield the MongoHistogram objects (dicts) from the given collection."""
    for name, histo in collection.items():
        if name == "filelist":
            continue
        yield typing.cast(MongoHistogram, histo)


def get_mongo_filelist(collection: MongoCollection) -> Optional[FilelistList]:
    """Return the FilelistList object (list) from the given collection."""
    try:
        return collection["filelist"]["files"]  # type: ignore
    except KeyError:
        return None


def check_type(
    value: Any,
    type_: Union[type, Tuple[type, ...]],
    member_type: Optional[Union[type, Tuple[type, ...]]] = None,
) -> Any:
    """Raise `TypeError` if `value` not of type, `type_`.

    Type check collection members by passing an iterable `value` and
    `member_type`.
    """
    if not isinstance(value, type_):
        raise TypeError(f"Attribute should be {type_} not {type(value)}")
    if member_type:
        for member in value:
            if not isinstance(member, member_type):
                raise TypeError(
                    f"Attribute member type should be {member_type} not {type(member)}"
                )
    return value


class I3Histogram:  # pylint: disable=R0902
    """A representation of a histogram."""

    # pylint: disable=R0913
    def __init__(
        self,
        name: str,
        xmax: Num,
        xmin: Num,
        overflow: int,
        underflow: int,
        nan_count: int,
        bin_values: List[Num],
    ) -> None:
        self.name = name
        self.xmax = xmax
        self.xmin = xmin
        self.overflow = overflow
        self.underflow = underflow
        self.nan_count = nan_count
        self.bin_values = bin_values

        self.history = []

    @property
    def name(self) -> str:
        """Histogram name."""
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value == "filelist":
            raise NameError("histogram cannot be named 'filelist'")
        check_type(value, str)
        self.__name = value

    @property
    def xmax(self) -> Num:
        """Histogram x-max value."""
        return self.__xmax

    @xmax.setter
    def xmax(self, value: Num) -> None:
        check_type(value, typing.get_args(Num))
        self.__xmax = value

    @property
    def xmin(self) -> Num:
        """Histogram x-min value."""
        return self.__xmin

    @xmin.setter
    def xmin(self, value: Num) -> None:
        check_type(value, typing.get_args(Num))
        self.__xmin = value

    @property
    def overflow(self) -> int:
        """Histogram overflow value."""
        return self.__overflow

    @overflow.setter
    def overflow(self, value: int) -> None:
        check_type(value, int)
        self.__overflow = value

    @property
    def underflow(self) -> int:
        """Histogram underflow value."""
        return self.__underflow

    @underflow.setter
    def underflow(self, value: int) -> None:
        check_type(value, int)
        self.__underflow = value

    @property
    def nan_count(self) -> int:
        """Histogram NaN count."""
        return self.__nan_count

    @nan_count.setter
    def nan_count(self, value: int) -> None:
        check_type(value, int)
        self.__nan_count = value

    @property
    def bin_values(self) -> List[Num]:
        """Histogram data bin values."""
        return self.__bin_values

    @bin_values.setter
    def bin_values(self, value: List[Num]) -> None:
        check_type(value, list, typing.get_args(Num))
        self.__bin_values = value

    @property
    def history(self) -> List[Num]:
        """Histogram database-write history."""
        return self.__history

    @history.setter
    def history(self, value: List[Num]) -> None:
        check_type(value, list, typing.get_args(Num))
        self.__history = value

    @staticmethod
    def from_dict(
        dict_: MongoHistogram,
    ) -> "I3Histogram":  # https://github.com/python/typing/issues/58
        """Create a Histogram instance from a dict. Factory method.

        `dict_` must have correctly typed items and cannot have extra keys/fields.

        Arguments:
            dict_ {MongoHistogram} -- the dictionary to be morphed

        Returns:
            [type] -- [description]

        Raises:
            NameError -- if the name field is illegal
            AttributeError -- if there's any extra keys (fields)
            TypeError -- if there's any mistyped items (attributes)
        """
        try:
            i3histogram = I3Histogram(
                dict_["name"],
                dict_["xmax"],
                dict_["xmin"],
                dict_["overflow"],
                dict_["underflow"],
                dict_["nan_count"],
                dict_["bin_values"],
            )
        except KeyError as e:
            raise AttributeError(f"histogram has missing field {str(e)}")

        # add extra items
        mandatory_keys = [
            "name",
            "xmax",
            "xmin",
            "overflow",
            "underflow",
            "nan_count",
            "bin_values",
        ]
        for attr_name, attr_value in dict_.items():
            if attr_name not in mandatory_keys:
                i3histogram.__setattr__(attr_name, attr_value)

        return i3histogram

    def to_dict(self, exclude: Optional[List[str]] = None) -> MongoHistogram:
        """Return attributes as dictionary."""
        dict_ = copy.deepcopy(vars(self))

        # remove class-property prefix from keys
        prefix = "_I3Histogram__"
        properties = [k for k in dict_ if k.startswith(prefix)]
        for p in properties:
            dict_[p[len(prefix) :]] = dict_.pop(p)

        # remove keys in `exclude`
        if exclude:
            for key in exclude:
                if key in dict_:
                    del dict_[key]

        return typing.cast(MongoHistogram, dict_)

    def add_to_history(self, pseudo_first: bool = False) -> None:
        """Append epoch timestamp to `history`.

        Keyword arguments:
            pseudo_first -- add 0.0 if `history` is empty (default: {False})
        """
        if not self.history and pseudo_first:
            self.history = [
                0.0
            ]  # must be old histogram, so it didn't come with a history
        self.history.append(time.time())

    def update(self, new_histo: "I3Histogram") -> None:
        """Update/increment/replace attribute values with those in `new_histo`.

        Append epoch timestamp to `history`.
        """
        for attr_name, attr_value in new_histo.to_dict().items():
            if attr_name == "bin_values":
                bin_values = [
                    b1 + b2 for b1, b2 in zip(self.bin_values, new_histo.bin_values)
                ]
                self.bin_values = bin_values
            elif attr_name == "overflow":
                self.overflow += new_histo.overflow
            elif attr_name == "underflow":
                self.underflow += new_histo.underflow
            elif attr_name == "nan_count":
                self.nan_count += new_histo.nan_count
            elif attr_name == "history":
                self.add_to_history(pseudo_first=True)
            else:
                self.__setattr__(attr_name, attr_value)
