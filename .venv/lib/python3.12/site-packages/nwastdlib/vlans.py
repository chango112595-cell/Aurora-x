# Copyright 2019-2025 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import annotations

import itertools
import operator
from collections import abc
from collections.abc import Iterable, Iterator, Sequence
from functools import reduce, total_ordering
from typing import AbstractSet, Any, ClassVar, cast

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, SchemaSerializer, core_schema

VLAN_RANGE_JSON_SCHEMA_REGEX = r"^(?:[1-9]\d{0,2}|[1-4]\d{3})(?:-(?:[1-9]\d{0,2}|[1-4]\d{3}))?(?:\s*,\s*(?:[1-9]\d{0,2}|[1-4]\d{3})(?:-(?:[1-9]\d{0,2}|[1-4]\d{3}))?)*$"


def to_ranges(i: Iterable[int]) -> Iterable[range]:
    """Convert a sorted iterable of ints to an iterable of range objects.

    IMPORTANT: the iterable passed in should be sorted and not contain duplicate elements.

    Examples::
        >>> list(to_ranges([2, 3, 4, 5, 7, 8, 9, 45, 46, 47, 49, 51, 53, 54, 55, 56, 57, 58, 59, 60, 61]))
        [range(2, 6), range(7, 10), range(45, 48), range(49, 50), range(51, 52), range(53, 62)]

    Args:
        i: sorted iterable

    Yields:
        range object for each consecutive set of integers

    """
    # The trick here is the key function (the lambda one) that calculates the difference between an element of the
    # iterable `i` and its corresponding enumeration value. For consecutive values in the iterable, this difference
    # will be the same! All these values (those with the same difference) are grouped by the `groupby` function. We
    # return the first and last element to construct a `range` object
    for _, g in itertools.groupby(enumerate(i), lambda t: t[1] - t[0]):
        group = list(g)
        yield range(group[0][1], group[-1][1] + 1)


def expand_ranges(ranges: Sequence[Sequence[int]], inclusive: bool = False) -> list[int]:
    """Expand sequence of range definitions into sorted and deduplicated list of individual values.

    A range definition is either a:

    * one element sequence -> an individual value.
    * two element sequence -> a range of values (either inclusive or exclusive).

    >>> expand_ranges([[1], [2], [10, 12]])
    [1, 2, 10, 11]
    >>> expand_ranges([[1], [2], [10, 12]], inclusive=True)
    [1, 2, 10, 11, 12]
    >>> expand_ranges([[]])
    Traceback (most recent call last):
        ...
    ValueError: Expected 1 or 2 element list for range definition. Got f0 element list instead.

    Resulting list is sorted::

        >>> expand_ranges([[100], [1, 4]], inclusive=True)
        [1, 2, 3, 4, 100]

    Args:
        ranges: sequence of range definitions
        inclusive: are the stop values of the range definition inclusive or exclusive.

    Returns:
        Sorted deduplicated list of individual values.

    Raises:
        ValueError: if range definition is not a one or two element sequence.

    """
    values: set[int] = set()
    for r in ranges:
        if len(r) == 2:
            values.update(range(r[0], r[1] + (1 if inclusive else 0)))
        elif len(r) == 1:
            values.add(r[0])
        else:
            raise ValueError(f"Expected 1 or 2 element list for range definition. Got f{len(r)} element list instead.")
    return sorted(values)


@total_ordering
class VlanRanges(abc.Set):
    """Represent VLAN ranges.

    This class is quite liberal in what it accepts as valid VLAN ranges. All of:

    - overlapping ranges
    - ranges with start value > stop value
    - ranges with extraneous whitespace

    are all accepted and normalized to a canonical value.

    Examples::

        # These are all equivalent
        VlanRanges("4,10-12,11-14")
        VlanRanges("4,  ,11 - 14, 10-  12")
        VlanRanges("4,10-14")
        VlanRanges([4, 10, 11, 12, 13, 14])
        VlanRanges([[4], [10,12], [11,14]])
        VlanRanges([(4, 4), (10, 14)])

    """

    __pydantic_serializer__: ClassVar[SchemaSerializer | None]  # workaround for a bug, see usage below

    _vlan_ranges: tuple[range, ...]

    def __init__(self, val: str | int | Iterable[int] | Sequence[Sequence[int]] | None = None) -> None:  # noqa: C901
        # The idea is to bring all acceptable values to one canonical intermediate format: the `Sequence[Sequence[
        # int]]`. Where the inner sequence is either a one or two element sequence. The one element sequence
        # represents a single VLAN, the two element sequence represents a VLAN range.
        #
        # An example of this intermediate format is::
        #
        #     vlans = [[5], [10, 12]]
        #
        # That example represents 4 VLANs, namely: 5, 10, 11, 12. The latter three VLANs are encode as a range.
        #
        # This intermediate format happens to be the format as accepted by :func:`expand_ranges`. This function has
        # the advantage of deduplicating overlapping ranges or VLANs specified more than once. In addition its return
        # value can be use as input to the :func:`to_ranges` function.
        vlans: Sequence[Sequence[int]] = []
        if val is None:
            self._vlan_ranges = ()
            return
        elif isinstance(val, str):  # noqa: RET505
            if val.strip() != "":
                # This might look complex, but it does handle strings such as `"  3, 4, 6-9, 4, 8 - 10"`
                try:
                    vlans = [[int(n) for n in s.strip().split("-")] for s in val.split(",")]
                except ValueError:
                    raise ValueError(f"{val} could not be converted to a {self.__class__.__name__} object.")
        elif isinstance(val, int):
            vlans = [[val]]
        elif isinstance(val, abc.Sequence):
            if len(val) > 0:
                if isinstance(val[0], int):
                    vlans = [[x] for x in val]  # type: ignore
                elif isinstance(val[0], abc.Sequence):
                    vlans = cast(Sequence[Sequence[int]], val)
        elif isinstance(val, abc.Iterable):
            vlans = [[x] for x in val]  # type: ignore
        else:
            raise ValueError(f"{val} could not be converted to a {self.__class__.__name__} object.")

        er = expand_ranges(vlans, inclusive=True)
        if er and not (er[0] >= 0 and er[-1] <= 4096):
            raise ValueError(f"{val} is out of range (0-4096).")

        self._vlan_ranges = tuple(to_ranges(er))

    def to_list_of_tuples(self) -> list[tuple[int, int]]:
        """Construct list of tuples representing the VLAN ranges.

        Example::

            >>> VlanRanges("10 - 12, 8").to_list_of_tuples()
            [(8, 8), (10, 12)]

        Returns:
            The VLAN ranges as contained in this object.

        """
        # `range` objects have an exclusive `stop`. VlanRanges is expressed using terms that use an inclusive stop,
        # which is one less then the exclusive one we use for the internal representation. Hence the `-1`
        return [(vr.start, vr.stop - 1) for vr in self._vlan_ranges]

    def __contains__(self, key: object) -> bool:
        return any(key in range_from_self for range_from_self in self._vlan_ranges)

    def __iter__(self) -> Iterator[int]:
        # The power of choosing proper abstractions: `range` objects already define an __iter__ method. Hence all we
        # need to do, is delegated to them.
        for vr in self._vlan_ranges:
            yield from vr

    def __len__(self) -> int:
        """Return the number of VLANs represented by this VlanRanges object.

        Returns:
            Number of VLAN's

        """
        # Utilize the __iter__ method
        return sum(1 for _ in self)

    def __str__(self) -> str:
        # `range` objects have an exclusive `stop`. VlanRanges is expressed using terms that use an inclusive stop,
        # which is one less then the exclusive one we use for the internal representation. Hence the `-1`
        return ",".join(str(vr.start) if len(vr) == 1 else f"{vr.start}-{vr.stop - 1}" for vr in self._vlan_ranges)

    def __repr__(self) -> str:
        # Note: we can't use self.__class__.__name__ here since we want to use the name of the annotated class
        return f"VlanRanges({str(self.to_list_of_tuples())})"

    def __json__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return self._vlan_ranges == o._vlan_ranges

    def __hash__(self) -> int:
        return hash(self._vlan_ranges)

    def __sub__(self, other: int | AbstractSet[Any]) -> VlanRanges:
        if isinstance(other, int):
            new_set = set(self)
            new_set.remove(other)
            return VlanRanges(new_set)
        return VlanRanges(set(self) - set(other))

    def __and__(self, other: AbstractSet[Any]) -> VlanRanges:
        return VlanRanges(set(self) & set(other))

    def __or__(self, other: AbstractSet[Any]) -> VlanRanges:
        return VlanRanges(set(self) | set(other))

    def __xor__(self, other: AbstractSet[Any]) -> VlanRanges:
        return VlanRanges(set(self) ^ set(other))

    def isdisjoint(self, other: Iterable[Any]) -> bool:
        return set(self).isdisjoint(other)

    def union(self, *others: AbstractSet[Any]) -> VlanRanges:
        return reduce(operator.__or__, others, self)

    @property
    def is_single_vlan(self) -> bool:
        try:
            int(str(self))
            return True
        except ValueError:
            return False

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema:
        schema = core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
                when_used="json",
            ),
        )
        # Workaround for bug https://github.com/pydantic/pydantic/issues/7779 to serialize custom class
        cls.__pydantic_serializer__ = SchemaSerializer(schema)
        return schema

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema_: CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(core_schema_)
        json_schema_resolved = handler.resolve_ref_schema(json_schema)
        schema_override = {
            "type": "string",
            "format": "vlan",
            "pattern": VLAN_RANGE_JSON_SCHEMA_REGEX,
            "examples": ["345", "20-23,45,50-100"],
        }
        return json_schema_resolved | schema_override

    @staticmethod
    def _validate(input_value: str | VlanRanges) -> VlanRanges:
        if isinstance(input_value, VlanRanges):
            return input_value
        return VlanRanges(input_value)

    @staticmethod
    def _serialize(value: VlanRanges) -> str:
        return str(value)
