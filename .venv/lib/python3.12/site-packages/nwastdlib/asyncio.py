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
import asyncio
import warnings
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

A = TypeVar("A")
R = TypeVar("R")

try:
    from anyio import CapacityLimiter, to_thread
except ImportError:
    warnings.warn("anyio is required for gather_nice_sync()", stacklevel=1)
else:

    async def gather_nice_sync(
        function: Callable[[A], R],
        args: Iterable[A],
        limit: int = 5,
        return_exceptions: bool = False,
    ) -> list[R | BaseException]:
        """Run function in thread for each args, using asyncio.gather() with limited concurrency.

        Example:
            def my_function(arg):
                ...

            await gather_nice_sync(my_function, ["id1", "id2", "id3"])

            def my_function_2(arg1, arg2):
                ...

            await gather_nice_sync(my_function_2, [("arg10", "arg11"), ("arg20", "arg21")])

        """

        def make_args(func_args: Iterable | object) -> Iterable:
            # When one argument is passed, wrap it in a list so run_sync can unpack it again
            if not isinstance(func_args, (tuple, list, set)):
                return [func_args]
            return func_args

        limiter = CapacityLimiter(limit)
        tasks = [to_thread.run_sync(function, *make_args(arg), limiter=limiter) for arg in args]
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)


async def gather_nice(
    coros: Iterable[Awaitable[R]],
    limit: int = 5,
    return_exceptions: bool = False,
) -> Iterable[R | BaseException]:
    """Run coroutines in asyncio.gather() with limited concurrency.

    Example:
       async def my_coroutine(arg):
           ...

       await gather_nice([my_coroutine(i) for i in ["id1", "id2", "id3"]])  # noqa: RST213

    """
    semaphore = asyncio.Semaphore(limit)

    async def sem_coro(coro: Awaitable[R]) -> R:
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros), return_exceptions=return_exceptions)
