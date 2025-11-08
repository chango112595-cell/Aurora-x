# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.

from collections.abc import Callable
from typing import Any

# Type annotations
ParseFloat = Callable[[str], Any]
Key = tuple[str, ...]
Pos = int
