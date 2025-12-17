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
from collections.abc import Callable
from enum import StrEnum, auto
from typing import Any

import asyncstdlib
import strawberry
import structlog
from fastapi import HTTPException
from graphql.pyutils import Path
from starlette.requests import Request
from strawberry import BasePermission
from strawberry.fastapi import BaseContext
from strawberry.types import Info
from strawberry.types.fields.resolver import StrawberryResolver
from strawberry.types.info import RootValueType

from oauth2_lib.fastapi import AuthManager, HttpBearerExtractor, OIDCUserModel
from oauth2_lib.settings import oauth2lib_settings

logger = structlog.get_logger(__name__)


class OauthContext(BaseContext):
    def __init__(
        self,
        auth_manager: AuthManager,
    ):
        self.auth_manager = auth_manager
        super().__init__()

    @asyncstdlib.cached_property
    async def get_current_user(self) -> OIDCUserModel | None:
        """Retrieve the OIDCUserModel once per graphql request.

        Note:
            This function should not raise exceptions, otherwise it will not be cached.
        """
        if not isinstance(self.request, Request):  # it could be None or a WebSocket
            logger.debug("Can't retrieve OIDCUserModel without a starlette Request", request_type=type(self.request))
            return None

        if not oauth2lib_settings.OAUTH2_ACTIVE:
            logger.debug("Not retrieving OIDCUserModel because OAUTH2_ACTIVE=False")
            return None

        try:
            http_bearer_extractor = HttpBearerExtractor(auto_error=False)
            http_authorization_credentials = await http_bearer_extractor(self.request)

            token = http_authorization_credentials.credentials if http_authorization_credentials else None
            return await self.auth_manager.authentication.authenticate(self.request, token)
        except HTTPException as exc:
            logger.debug("User is not authenticated", status_code=exc.status_code, detail=exc.detail)
            return None


OauthInfo = Info[OauthContext, RootValueType]


def get_path_as_string(path: Path) -> str:
    if path.prev:
        return f"{get_path_as_string(path.prev)}/{path.key}"
    return f"{path.key}"


def get_query_path(info: OauthInfo) -> str:
    service_name = oauth2lib_settings.SERVICE_NAME
    service_name_path = f"/{service_name}" if service_name else ""
    return f"{service_name_path}/{get_path_as_string(info.path)}/".lower()


def get_mutation_path(info: OauthInfo) -> str:
    service_name = oauth2lib_settings.SERVICE_NAME
    service_name_path = f"/{service_name}" if service_name else ""
    return f"{service_name_path}/{info.path.key}"


def skip_mutation_auth_checks() -> bool:
    is_exception = oauth2lib_settings.ENVIRONMENT in oauth2lib_settings.ENVIRONMENT_IGNORE_MUTATION_DISABLED
    logger.debug(
        "Mutations are disabled",
        OAUTH2_ACTIVE=oauth2lib_settings.OAUTH2_ACTIVE,
        OAUTH2_AUTHORIZATION_ACTIVE=oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE,
        MUTATIONS_ENABLED=oauth2lib_settings.MUTATIONS_ENABLED,
        is_exception=is_exception,
    )
    return is_exception


async def is_authenticated(info: OauthInfo) -> bool:
    """Check that the user has a valid and active authentication token."""
    current_user = await info.context.get_current_user
    return current_user is not None


async def is_authorized(info: OauthInfo, path: str, method: str) -> bool:
    """Check that the user is allowed to query/mutate this path."""
    context = info.context
    current_user = await context.get_current_user
    if not current_user:
        return False

    authorization_decision = await context.auth_manager.graphql_authorization.authorize(path, method, current_user)
    authorized = bool(authorization_decision)
    logger.debug(
        "Received graphql authorization decision",
        path=path,
        authorization_decision=authorization_decision,
        is_authorized=authorized,
    )

    return authorized


class ErrorType(StrEnum):
    """Subset of the ErrorType enum in nwa-stdlib."""

    NOT_AUTHENTICATED = auto()
    NOT_AUTHORIZED = auto()


class IsAuthenticatedForQuery(BasePermission):
    message = "User is not authenticated"
    error_extensions = {"error_type": ErrorType.NOT_AUTHENTICATED}

    async def has_permission(self, source: Any, info: OauthInfo, **kwargs) -> bool:  # type: ignore
        if not oauth2lib_settings.OAUTH2_ACTIVE:
            logger.debug(
                "Authentication disabled",
                OAUTH2_ACTIVE=oauth2lib_settings.OAUTH2_ACTIVE,
                OAUTH2_AUTHORIZATION_ACTIVE=oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE,
            )
            return True

        return await is_authenticated(info)


class IsAuthenticatedForMutation(BasePermission):
    message = "User is not authenticated"
    error_extensions = {"error_type": ErrorType.NOT_AUTHENTICATED}

    async def has_permission(self, source: Any, info: OauthInfo, **kwargs) -> bool:  # type: ignore
        mutations_active = oauth2lib_settings.OAUTH2_ACTIVE and oauth2lib_settings.MUTATIONS_ENABLED
        if not mutations_active:
            return skip_mutation_auth_checks()

        return await is_authenticated(info)


class IsAuthorizedForQuery(BasePermission):
    error_extensions = {"error_type": ErrorType.NOT_AUTHORIZED}

    async def has_permission(self, source: Any, info: OauthInfo, **kwargs) -> bool:  # type: ignore
        if not (oauth2lib_settings.OAUTH2_ACTIVE and oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE):
            logger.debug(
                "Authorization disabled",
                OAUTH2_ACTIVE=oauth2lib_settings.OAUTH2_ACTIVE,
                OAUTH2_AUTHORIZATION_ACTIVE=oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE,
            )
            return True

        path = get_query_path(info)
        if await is_authorized(info, path, "QUERY"):
            return True

        self.message = f"User is not authorized to query `{path}`"
        return False


class IsAuthorizedForMutation(BasePermission):
    error_extensions = {"error_type": ErrorType.NOT_AUTHORIZED}

    async def has_permission(self, source: Any, info: OauthInfo, **kwargs) -> bool:  # type: ignore
        mutations_active = (
            oauth2lib_settings.OAUTH2_ACTIVE
            and oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE
            and oauth2lib_settings.MUTATIONS_ENABLED
        )
        if not mutations_active:
            return skip_mutation_auth_checks()

        path = get_mutation_path(info)
        if await is_authorized(info, path, "POST"):
            return True

        self.message = f"User is not authorized to execute mutation `{path}`"
        return False


def authenticated_field(
    description: str,
    resolver: StrawberryResolver | Callable | staticmethod | classmethod | None = None,
    deprecation_reason: str | None = None,
    permission_classes: list[type[BasePermission]] | None = None,
) -> Any:
    permissions = permission_classes if permission_classes else []
    return strawberry.field(
        description=description,
        resolver=resolver,  # type: ignore
        deprecation_reason=deprecation_reason,
        permission_classes=[IsAuthenticatedForQuery, IsAuthorizedForQuery] + permissions,
    )


def authenticated_mutation_field(
    description: str,
    resolver: StrawberryResolver | Callable | staticmethod | classmethod | None = None,
    deprecation_reason: str | None = None,
    permission_classes: list[type[BasePermission]] | None = None,
) -> Any:
    permissions = permission_classes if permission_classes else []
    return strawberry.field(
        description=description,
        resolver=resolver,  # type: ignore
        deprecation_reason=deprecation_reason,
        permission_classes=[IsAuthenticatedForMutation, IsAuthorizedForMutation] + permissions,
    )


def authenticated_federated_field(  # type: ignore
    description: str,
    resolver: StrawberryResolver | Callable | staticmethod | classmethod | None = None,
    deprecation_reason: str | None = None,
    requires: list[str] | None = None,
    permission_classes: list[type[BasePermission]] | None = None,
    **kwargs,
) -> Any:
    permissions = permission_classes if permission_classes else []
    return strawberry.federation.field(
        description=description,
        resolver=resolver,  # type: ignore
        deprecation_reason=deprecation_reason,
        permission_classes=[IsAuthenticatedForQuery, IsAuthorizedForQuery] + permissions,
        requires=requires,
        **kwargs,
    )
