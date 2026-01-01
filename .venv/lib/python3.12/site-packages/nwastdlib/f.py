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
#

from collections.abc import Callable
from typing import Any, TypeVar

α = TypeVar("α")
β = TypeVar("β")
γ = TypeVar("γ")


def identity(x: α) -> α:
    """Return the first argument.

    This is usefull in function that accept an function

    >>> identity("A")
    'A'
    """
    return x


def const(x: α) -> Callable[[Any], α]:
    """Convert a value `x` to a function that always results in `x`.

    >>> const(1)(2)
    1
    >>> const(1)("foo")
    1
    >>> const(1)(None)
    1
    """
    return lambda *_: x
