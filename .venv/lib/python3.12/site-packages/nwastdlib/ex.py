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

"""Module containing functions to deal with `Exception`s."""


import traceback


def show_ex(ex: Exception, stacklimit: int | None = None) -> str:
    """Show an exception, including its class name, message and (limited) stacktrace.

    >>> try:
    ...     raise Exception("Something went wrong")
    ... except Exception as e:
    ...     print(show_ex(e))
    Exception: Something went wrong
    ...
    """
    tbfmt = "".join(traceback.format_tb(ex.__traceback__, stacklimit))
    return f"{type(ex).__name__}: {ex}\n{tbfmt}"
