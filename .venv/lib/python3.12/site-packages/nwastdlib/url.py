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

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlencode


class URL(str):
    r"""Helper class for conveniently constructing URLs.

    To that end the `/` operator has been overloaded to append path elements. Similarly the `//` operator has
    been overloaded to easily add a query string to the URL.

    Being a subclass of `str`, instances of `URL` can be used anywhere a `str` is expected.

    *IMPORTANT* No form of verification is performed. Meaning for instance that any string, not only those that
    actually make up an URL, can be use to initialize an URL instance. And one can add multiple query strings to an
    URL instance leading to an improperly formatted URL.

    Example::
            >>> base_url = URL("http://example.org/")

            >>> str(base_url)
            'http://example.org/'
            >>> repr(base_url)
            "URL('http://example.org/')"

            >>> base_url / "/api"  == base_url / "api"
            True

            >>> api_url = base_url / "api"
            >>> str(api_url)
            'http://example.org/api'

            >>> url = api_url / "ip" / "address" // {"version": 4}
            >>> str(url)
            'http://example.org/api/ip/address?version=4'

            >>> # paths don't need to be strings
            >>> url = api_url / 1 / 2 / 3
            >>> str(url)
            'http://example.org/api/1/2/3'

            >>> # query string properly url encoded?
            >>> url = api_url // {"query": ' "%-.<>\\^_`{|}~'}
            >>> str(url)
            'http://example.org/api?query=+%22%25-.%3C%3E%5C%5E_%60%7B%7C%7D~'



    """

    def __truediv__(self, path: object) -> URL:
        """Append path element to the URL object.

        It prevents accidental inclusion of too many slashes between the appended path elements should the
        URL end in a slash and/or the `path` element start with a slash.

        Args:
            path: path element to append

        Returns:
            A new URL object with the `path` element appended.

        """
        if not isinstance(path, str):
            path = str(path)
        return URL(self.rstrip("/") + "/" + path.lstrip("/"))

    def __floordiv__(self, query: Mapping) -> URL:
        """Append a query string to the URL.

        Args:
            query: Mapping of values that should be converted to a query string.

        Returns:
            a new URL object with the `query` appended as a query string.

        """
        params = urlencode(query)
        return URL(f"{self}?{params}")

    def __repr__(self) -> str:
        return f"URL('{self}')"
