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
import datetime
import hashlib
import hmac
import inspect
import pickle  # noqa: S403
import sys
import types
import typing
import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol, get_args, get_origin, runtime_checkable
from uuid import UUID

import structlog
from redis.asyncio import Redis as AIORedis

logger = structlog.get_logger(__name__)


@runtime_checkable
class SerializerProtocol(Protocol):
    """Abstract base class to specifies how to build yur own serializer."""

    @staticmethod
    def deserialize(data: Any) -> Any: ...

    @staticmethod
    def serialize(data: Any) -> Any: ...


class DefaultSerializer:
    """Implementation of the default protocol that uses pickle."""

    @staticmethod
    def deserialize(data: Any) -> Any:
        return pickle.loads(data)  # noqa: S301

    @staticmethod
    def serialize(data: bytes | bytearray | str) -> Any:
        return pickle.dumps(data)


def _deserialize(data: Any, serializer: SerializerProtocol) -> Any:
    try:
        data = serializer.deserialize(data)
    except Exception as e:
        logger.error(
            "Cache deserialization failed, returning None, so cache will be overwritten with a new value", error=e
        )
        return None
    return data


def get_hmac_checksum(secret: str, message: bytes | bytearray | str) -> str:
    if isinstance(message, str):
        message = message.encode()
    h = hmac.new(secret.encode(), message, hashlib.sha512)
    return h.hexdigest()


async def set_cache_value(
    pool: AIORedis, cache_key: str, value: Any, expiry_seconds: int, serializer: SerializerProtocol
) -> None:
    await pool.setex(cache_key, expiry_seconds, serializer.serialize(value))


async def get_cache_value(pool: AIORedis, cache_key: str, serializer: SerializerProtocol) -> Any:
    serialized_value = await pool.get(cache_key)
    return None if serialized_value is None else _deserialize(serialized_value, serializer)


async def set_signed_cache_value(
    pool: AIORedis, secret: str, cache_key: str, value: Any, expiry_seconds: int, serializer: SerializerProtocol
) -> None:
    pickled_value = serializer.serialize(value)
    checksum = get_hmac_checksum(secret, pickled_value)
    pipeline = pool.pipeline()
    pipeline.setex(cache_key, expiry_seconds, pickled_value).setex(
        f"{cache_key}-checksum", expiry_seconds, checksum.encode()
    )
    result_set_cache_value, result_set_cache_checksum = await pipeline.execute()
    if not result_set_cache_value or not result_set_cache_checksum:
        logger.warning(
            "Cache not set", cache_key=cache_key, value_ok=result_set_cache_value, checksum_ok=result_set_cache_checksum
        )


async def get_signed_cache_value(pool: AIORedis, secret: str, cache_key: str, serializer: SerializerProtocol) -> Any:
    pipeline = pool.pipeline()
    pipeline.get(cache_key).get(f"{cache_key}-checksum")
    pickled_value, cache_checksum = await pipeline.execute()
    if not pickled_value or not cache_checksum:
        return None

    cache_checksum = cache_checksum.decode("utf-8")
    if (checksum := get_hmac_checksum(secret, pickled_value)) != cache_checksum:
        logger.error(
            "Checksum for cache was wrong, someone tampered with the values!",
            correct_checksum=str(cache_checksum),
            recalculated_checksum=checksum,
        )
        return None
    return _deserialize(pickled_value, serializer)


def _generate_cache_key_suffix(*, skip_first: bool, args: tuple, kwargs: dict) -> str | None:
    # Auto generate cache key suffix based on the arguments
    # Note: this makes no attempt to handle non-hashable values like lists and sets or other complex objects
    filtered_args = args[int(skip_first) :]
    filtered_kwargs = frozenset(kwargs.items())
    if not filtered_args and not filtered_kwargs:
        return None
    args_and_kwargs_string = (filtered_args, filtered_kwargs)
    return str(args_and_kwargs_string)


SAFE_CACHED_RESULT_TYPES = (
    int,
    str,
    float,
    datetime.datetime,
    UUID,
)


def _unwrap_type(type_: Any) -> Any:
    origin, args = get_origin(type_), get_args(type_)
    # 'str'
    if not origin:
        return type_

    # 'str | None' or 'Optional[str]'
    if origin in (types.UnionType, typing.Union) and types.NoneType in args:
        return args[0]

    # For more advanced type handling, see https://github.com/workfloworchestrator/nwa-stdlib/issues/45
    return type_


def _format_warning(func: Callable, name: str, type_: Any) -> str:
    safe_types = (t.__name__ for t in SAFE_CACHED_RESULT_TYPES)
    return (
        f"{cached_result.__name__}() applied to function {func.__qualname__} which has parameter '{name}' "
        f"of unsafe type '{type_.__name__}'. "
        f"This can lead to duplicate keys and thus cache misses. "
        f"To resolve this, either set a static keyname or only use parameters of the type {safe_types}. "
        f"If you understand the risks you can suppress/ignore this warning. "
        f"For background and feedback see https://github.com/workfloworchestrator/nwa-stdlib/issues/45"
    )


def _validate_signature(func: Callable) -> bool:
    """Validate the function's signature and return a bool whether to skip the first argument.

    Raises warnings for potentially unsafe cache key arguments.
    """
    func_params = inspect.signature(func).parameters
    is_nested_function = "." in func.__qualname__

    skip_first_arg = False
    for idx, (name, param) in enumerate(func_params.items()):
        if idx == 0 and name == "self" and is_nested_function:
            # This will falsely recognize a closure function with 'self'
            # as first arg as a method. Nothing we can do about that..
            skip_first_arg = True
            continue

        param_type = _unwrap_type(param.annotation)
        if param_type not in SAFE_CACHED_RESULT_TYPES:
            warnings.warn(_format_warning(func, name, param.annotation), stacklevel=2)
    return skip_first_arg


def _validate_coroutine(func: Callable) -> None:
    """Validate that the callable is a coroutine."""
    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"Can't apply {cached_result.__name__}() to {func.__name__}: not a coroutine")


def cached_result(
    pool: AIORedis,
    prefix: str,
    secret: str | None,
    key_name: str | None = None,
    expiry_seconds: int = 120,
    serializer: SerializerProtocol = DefaultSerializer,
    revalidate_fn: Callable[..., bool] | None = None,
) -> Callable:
    """Pass returned result objects from a async function call into redis.

    Returns a decorator function that will cache every result of a function to redis. This only works
    for functions with string, int or UUID arguments and result objects that can be serialized by the
    python pickle library. When you provide a `secret` a second key will be stored, containing a checksum.
    That adds another layer of security to prevent malicious code from being executed when trying yo unpickle
    data that an attacker may have tampered with in Redis.

    When the result can be serialized to JSON, and you're using a fast JSON library, like `orjson` you should
    provide your own serializer. In that case you can also disable the hmac signing by providing `secret=None`.

    Note: Serialization errors will raise an Exception but deserialization will fail silently with only a logged error.


    Example:
        Decorate a suitable function with all the default settings like this:::
            @cached_result(pool, "your_app_name", "SECRET_KEY_FOR_HMAC_CHECKSUM")
            def my_cached_function(uuid_arg, string_arg, int_kwarg=1):
                return do_stuff(uuid_arg, string_arg, kwarg)

        The first call is cached and reused for 120s. If the defaults are inadequate use:::
            @cached_result(pool, "your_app_name", "SECRET_KEY_FOR_HMAC_CHECKSUM", "desired_cache_key_name", 1800)
            def my_other_function...

    Args:
        pool: A async redis cache pool.
        secret: used to generate a checksum too ensure cache tampering is not possible. Set to `None` to disable.
        prefix: Prefix for the cache keys generated.
        key_name: When specified the total redis key_name will be "prefix:key_name".
        expiry_seconds: expiration in seconds. Defaults to two minutes (120s).
        serializer: Provide your own Serializer class or use the default pickle.
        revalidate_fn: Callable function that returns bool whether to revalidate the cached result.

    Returns:
        decorator function

    """
    python_major, python_minor = sys.version_info[:2]
    prefix_version = f"{prefix}:{python_major}.{python_minor}"
    static_cache_key: str | None = f"{prefix_version}:{key_name}" if key_name else None

    def cache_decorator(func: Callable) -> Callable:
        _validate_coroutine(func)
        skip_first = _validate_signature(func)
        prefix_version_func = f"{prefix_version}:{func.__qualname__}".lower()

        @wraps(func)
        async def func_wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            from_cache = (not revalidate_fn(*args, **kwargs)) if revalidate_fn else True

            if static_cache_key:
                cache_key = static_cache_key
            elif suffix := _generate_cache_key_suffix(skip_first=skip_first, args=args, kwargs=kwargs):
                cache_key = f"{prefix_version_func}:{suffix}"
            else:
                cache_key = prefix_version_func

            if from_cache:
                logger.debug("Cache called with wrapper func", func_name=func.__name__, cache_key=cache_key)
                if secret:
                    if (cached_val := await get_signed_cache_value(pool, secret, cache_key, serializer)) is not None:
                        logger.info("Cache contains secure key, serving from cache", func_name=func.__name__)
                        return cached_val
                else:
                    if (cached_val := await get_cache_value(pool, cache_key, serializer)) is not None:
                        logger.info("Cache contains key, serving from cache", func_name=func.__name__)
                        return cached_val
                logger.info("Cache doesn't contain key, calling real function", func_name=func.__name__)
            else:
                logger.info("ignoring cache, calling real function", func_name=func.__name__)

            result = await func(*args, **kwargs)
            if secret:
                await set_signed_cache_value(pool, secret, cache_key, result, expiry_seconds, serializer)
            else:
                await set_cache_value(pool, cache_key, result, expiry_seconds, serializer)
            return result

        return func_wrapper

    return cache_decorator
