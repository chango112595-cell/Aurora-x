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
import ssl
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Mapping
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any, Optional, cast

from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from httpx import AsyncClient, NetworkError
from pydantic import BaseModel
from starlette.requests import ClientDisconnect, HTTPConnection
from starlette.status import HTTP_403_FORBIDDEN
from starlette.websockets import WebSocket
from structlog import get_logger

from oauth2_lib.settings import oauth2lib_settings

logger = get_logger(__name__)

HTTPX_SSL_CONTEXT = ssl.create_default_context()  # https://github.com/encode/httpx/issues/838


class OIDCUserModel(dict):
    """The standard claims of a OIDCUserModel object. Defined per `Section 5.1`_.

    .. _`Section 5.1`: http://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
    """

    #: registered claims that OIDCUserModel supports
    REGISTERED_CLAIMS = [
        "sub",
        "name",
        "given_name",
        "family_name",
        "middle_name",
        "nickname",
        "preferred_username",
        "profile",
        "picture",
        "website",
        "email",
        "email_verified",
        "gender",
        "birthdate",
        "zoneinfo",
        "locale",
        "phone_number",
        "phone_number_verified",
        "address",
        "updated_at",
    ]

    def __getattr__(self, key: str) -> Any:
        try:
            return object.__getattribute__(self, key)
        except AttributeError as error:
            if key in self.REGISTERED_CLAIMS:
                return self.get(key)
            raise error

    @property
    def user_name(self) -> str:
        return ""


RequestPath = str
AuthenticationFunc = Callable[[HTTPConnection, Optional[str]], Awaitable[Optional[dict]]]
AuthorizationFunc = Callable[[HTTPConnection, OIDCUserModel], Awaitable[bool]]
GraphqlAuthorizationFunc = Callable[[RequestPath, OIDCUserModel], Awaitable[Optional[bool]]]


class OIDCConfig(BaseModel):
    """Holds OpenID Connect provider configuration.

    Details include endpoints, supported features, and various supported specifications.
    """

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    introspect_endpoint: str | None = None
    introspection_endpoint: str | None = None
    jwks_uri: str
    response_types_supported: list[str]
    response_modes_supported: list[str]
    grant_types_supported: list[str]
    subject_types_supported: list[str]
    id_token_signing_alg_values_supported: list[str]
    scopes_supported: list[str]
    token_endpoint_auth_methods_supported: list[str]
    claims_supported: list[str]
    claims_parameter_supported: bool
    request_parameter_supported: bool
    code_challenge_methods_supported: list[str]


class OPAResult(BaseModel):
    """Represents an OPA decision result.

    Contains the decision outcome and an associated decision ID.
    """

    result: bool = False
    decision_id: str


class Authentication(ABC):
    """Abstract base for authentication mechanisms.

    Requires an async authenticate method implementation.
    """

    @abstractmethod
    async def authenticate(self, request: Request, token: str | None = None) -> dict | None:
        """Authenticate the user."""
        pass


class IdTokenExtractor(ABC):
    """Abstract base for ID token extraction.

    Must implement an async method to extract the token from requests.
    """

    @abstractmethod
    async def extract(self, request: Request) -> str | None:
        pass


class HttpBearerExtractor(HTTPBearer, IdTokenExtractor):
    """Extracts bearer tokens using FastAPI's HTTPBearer.

    Specifically designed for HTTP Authorization header token extraction.
    """

    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """Extract the Authorization header from the request."""
        return await super().__call__(request)

    async def extract(self, request: Request) -> str | None:
        """Extract the token from the Authorization header in the request."""
        http_auth_credentials = await super().__call__(request)

        return http_auth_credentials.credentials if http_auth_credentials else None


class OIDCAuth(Authentication):
    """Implements OIDC authentication.

    Manages token extraction and user information retrieval based on OIDC standards.
    """

    def __init__(
        self,
        openid_url: str,
        openid_config_url: str,
        resource_server_id: str,
        resource_server_secret: str,
        oidc_user_model_cls: type[OIDCUserModel],
    ):
        self.openid_url = openid_url
        self.openid_config_url = openid_config_url
        self.resource_server_id = resource_server_id
        self.resource_server_secret = resource_server_secret
        self.user_model_cls = oidc_user_model_cls

        self.openid_config: OIDCConfig | None = None

    async def authenticate(self, request: Request, token: str | None = None) -> OIDCUserModel | None:
        """Return the OIDC user from OIDC introspect endpoint.

        This is used as a security module in Fastapi projects

        Args:
            request: Starlette request/websocket method.
            token: Optional value to directly pass a token.

        Returns:
            OIDCUserModel object.

        """
        if not oauth2lib_settings.OAUTH2_ACTIVE:
            return None

        if await self.is_bypassable_request(request):
            return None

        if not token:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")

        async with AsyncClient(http1=True, verify=HTTPX_SSL_CONTEXT) as async_client:
            await self.check_openid_config(async_client)

            user_info: OIDCUserModel = await self.userinfo(async_client, token)
            logger.debug("OIDCUserModel object.", user_info=user_info)
            return user_info

    @staticmethod
    async def is_bypassable_request(request: Request) -> bool:
        """By default no request is bypassable."""
        return False

    async def userinfo(self, async_request: AsyncClient, token: str) -> OIDCUserModel:
        """Get the userinfo from the openid server.

        :param AsyncClient async_request: The async request
        :param str token: the access_token
        :return: OIDCUserModel dict: OIDC user model from openid server

        """
        raise NotImplementedError()

    async def check_openid_config(self, async_client: AsyncClient) -> None:
        """Check of openid config is loaded and load if not."""
        if self.openid_config is not None:
            return

        response = await async_client.get(self.openid_config_url)
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=f"Could not load openid config from {self.openid_config_url}",
            )
        self.openid_config = OIDCConfig(**response.json())


class Authorization(ABC):
    """Defines the authorization logic interface.

    Implementations must provide an async method to authorize based on request and user info.
    """

    @abstractmethod
    async def authorize(self, request: HTTPConnection, user: OIDCUserModel) -> bool | None:
        pass


class GraphqlAuthorization(ABC):
    """Defines the graphql authorization logic interface.

    Implementations must provide an async method to authorize based on request and user info.
    """

    @abstractmethod
    async def authorize(self, request: RequestPath, method: str, user: OIDCUserModel) -> bool | None:
        pass


class OPAMixin:
    """Base for OPA-based authorization logic.

    Supports getting and evaluating OPA policy decisions.
    """

    def __init__(self, opa_url: str, auto_error: bool = True, opa_kwargs: Mapping[str, Any] | None = None):
        self.opa_url = opa_url
        self.auto_error = auto_error
        self.opa_kwargs = opa_kwargs

    async def get_decision(self, async_client: AsyncClient, opa_input: dict) -> OPAResult:
        logger.debug("Posting input json to Policy agent", opa_url=self.opa_url, input=opa_input)
        try:
            result = await async_client.post(self.opa_url, json=opa_input)
        except (NetworkError, TypeError) as exc:
            logger.debug("Could not get decision from policy agent", error=str(exc))
            raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Policy agent is unavailable")

        json_result = result.json()
        logger.debug("Received decision from policy agent", decision=json_result)
        return OPAResult(**json_result)

    def evaluate_decision(self, decision: OPAResult, **context: dict[str, Any]) -> bool:
        did = decision.decision_id

        if decision.result:
            logger.debug("User is authorized to access the resource", decision_id=did, **context)
            return True

        logger.debug("User is not allowed to access the resource", decision_id=did, **context)
        if not self.auto_error:
            return False

        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=f"User is not allowed to access resource: {context.get('resource')} Decision was taken with id: {did}",
        )


class OPAAuthorization(Authorization, OPAMixin):
    """Applies OPA decisions to HTTP requests for authorization.

    Uses OAUTH2 settings and request information to authorize actions.
    """

    async def authorize(self, request: HTTPConnection, user_info: OIDCUserModel) -> bool | None:
        if not (oauth2lib_settings.OAUTH2_ACTIVE and oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE):
            return None

        try:
            if isinstance(request, WebSocket):
                json = {}
            else:
                request = cast(Request, request)
                json = await request.json()
        # Silencing the Decode error or Type error when request.json() does not return anything sane.
        # Some requests do not have a json response therefore as this code gets called on every request
        # we need to suppress the `None` case (TypeError) or the `other than json` case (JSONDecodeError)
        # Suppress AttributeError in case of websocket request, it doesn't have .json
        except (JSONDecodeError, TypeError, ClientDisconnect, AttributeError, RuntimeError) as e:
            if isinstance(e, RuntimeError) and "Stream consumed" not in str(e):
                # RuntimeError is a very broad error class. We only want to catch and ignore a stream
                # consumed runtime error. In other cases, reraise the error.
                raise e
            json = {}

        # defaulting to GET request method for WebSocket request, it doesn't have .method
        request_method = request.method if hasattr(request, "method") else "GET"
        opa_input = {
            "input": {
                **(self.opa_kwargs or {}),
                **(user_info or {}),
                "resource": request.url.path,
                "method": request_method,
                "arguments": {"path": request.path_params, "query": {**request.query_params}, "json": json},
            }
        }

        async with AsyncClient(http1=True, verify=HTTPX_SSL_CONTEXT) as async_request:
            decision = await self.get_decision(async_request, opa_input)

        context = {
            "resource": opa_input["input"]["resource"],
            "method": opa_input["input"]["method"],
            "user_info": user_info,
            "input": opa_input,
            "url": request.url,
        }
        return self.evaluate_decision(decision, **context)


class GraphQLOPAAuthorization(GraphqlAuthorization, OPAMixin):
    """Specializes OPA authorization for GraphQL operations.

    Customizable to handle partial results without raising HTTP 403.
    """

    def __init__(self, opa_url: str, auto_error: bool = False, opa_kwargs: Mapping[str, Any] | None = None):
        # By default don't raise HTTP 403 because partial results are preferred
        super().__init__(opa_url, auto_error, opa_kwargs)

    async def authorize(self, request: RequestPath, method: str, user_info: OIDCUserModel) -> bool | None:
        if not (oauth2lib_settings.OAUTH2_ACTIVE and oauth2lib_settings.OAUTH2_AUTHORIZATION_ACTIVE):
            return None

        opa_input = {
            "input": {
                **(self.opa_kwargs or {}),
                **(user_info or {}),
                "resource": request,
                "method": method,
            }
        }

        async with AsyncClient(http1=True, verify=HTTPX_SSL_CONTEXT) as async_request:
            decision = await self.get_decision(async_request, opa_input)

        context = {"resource": opa_input["input"]["resource"], "input": opa_input}
        return self.evaluate_decision(decision, **context)


class AuthManager:
    """Manages the authentication and authorization mechanisms for the application.

    This manager class orchestrates authentication and authorization, utilizing OpenID Connect (OIDC) and
    Open Policy Agent (OPA) respectively. It serves as a central hub for user authentication states and
    authorization policies. If defaults are insufficient, users can register alternatives or customize existing ones.

    Attributes:
        _authentication (OIDCAuth): Handles user authentication.
        _authorization (Authorization): Manages access controls.
        _graphql_authorization (GraphqlAuthorization): Manages GraphQL-specific authorization.

    Methods:
        authentication: Gets or sets the OIDCAuth instance, allowing customization of the authentication process.
        authorization: Gets or sets the Authorization instance, permitting customization of access controls.
        graphql_authorization: Gets or sets the GraphqlAuthorization instance, enabling specific security policies for GraphQL.
    """

    def __init__(self) -> None:
        self._authentication = OIDCAuth(
            openid_url=oauth2lib_settings.OIDC_BASE_URL,
            openid_config_url=oauth2lib_settings.OIDC_CONF_URL,  # Corrected parameter name
            resource_server_id=oauth2lib_settings.OAUTH2_RESOURCE_SERVER_ID,
            resource_server_secret=oauth2lib_settings.OAUTH2_RESOURCE_SERVER_SECRET,
            oidc_user_model_cls=OIDCUserModel,
        )
        self._authorization: Authorization = OPAAuthorization(opa_url=oauth2lib_settings.OPA_URL)
        self._graphql_authorization: GraphqlAuthorization = GraphQLOPAAuthorization(opa_url=oauth2lib_settings.OPA_URL)

    @property
    def authentication(self) -> OIDCAuth:
        return self._authentication

    @authentication.setter
    def authentication(self, auth_instance: OIDCAuth) -> None:
        self._authentication = auth_instance

    @property
    def authorization(self) -> Authorization:
        return self._authorization

    @authorization.setter
    def authorization(self, auth_instance: Authorization) -> None:
        self._authorization = auth_instance

    @property
    def graphql_authorization(self) -> GraphqlAuthorization:
        return self._graphql_authorization

    @graphql_authorization.setter
    def graphql_authorization(self, auth_instance: GraphqlAuthorization) -> None:
        self._graphql_authorization = auth_instance
