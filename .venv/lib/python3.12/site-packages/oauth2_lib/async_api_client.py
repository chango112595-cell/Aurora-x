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
from asyncio import new_event_loop
from http import HTTPStatus
from typing import Any

import structlog
from authlib.integrations.base_client import BaseOAuth

logger = structlog.get_logger(__name__)


def is_api_exception(ex: Exception) -> bool:
    """Test for swagger-codegen ApiException.

    For each API, swagger-codegen generates a new ApiException class. These are not organized into
    a hierarchy. Hence testing whether one is dealing with one of the ApiException classes without knowing how
    many there are and where they are located, needs some special logic.

    Args:
        ex: the Exception to be tested.

    Returns:
        True if it is an ApiException, False otherwise.

    """
    return ex.__class__.__name__ == "ApiException"


class AsyncAuthMixin:
    """Authorization mixin for swagger-codegen generated ApiClients.

    This mixin ensures the proper OAuth2 header is set for API calls if OAuth2 has been enabled. It will also try
    to refresh the token and retry the call if it expects the token to be expired.

    IMPORTANT: AsyncAuthMixin should be the first class in the inheritance list!

    Given a Fubar API. Usage is::

        import fubar_client

        class FubarApiClient(AuthMixin, fubar_client.ApiClient)
            pass

    Calls to the Fubar API can now be made as follows:

        from fubar_client import BlahApi

        fac = FubarApiClient('https://api.staging.automation.surf.net/fubar')
        foo = await BlaApi(fac).get_foo_by_id(foo_id)

    """

    _token: dict | None

    def __init__(
        self,
        oauth_client: BaseOAuth,
        oauth_client_name: str,
        oauth_active: bool,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._oauth_client: BaseOAuth = getattr(oauth_client, oauth_client_name)
        self._oauth_active = oauth_active
        self._token = None

    def add_client_creds_token_header(self, headers: dict[str, Any]) -> None:
        """Add header with credentials to an existing set of headers.

        This function assumes the `access_token` has been set in the application configuration
        by `refresh_client_creds_token or by acquire_token`.

        Args:
            headers: Existing set of headers that need to be extended with an Authorization header.

        Returns:
            New set of headers.

        """
        if not self._token and self._oauth_active:
            loop = new_event_loop()
            loop.run_until_complete(self.refresh_client_creds_token())
        if self._token:
            access_token = self._token
            headers["Authorization"] = f"bearer {access_token['access_token']}"

    async def refresh_client_creds_token(self, force: bool = False) -> None:
        """Conditionally fetch access_token.

        This method will either set the token if it is not set or reset the token if Force is added,
        otherwise it will just return.

        Args:
            force: Force the fetch, even if the access_token is already in the application configuration.

        """
        if self._token and not force:
            return

        logger.debug("Acquiring new access token", force=force)
        self._token = await self._oauth_client.fetch_access_token()

    def request(  # type:ignore
        self,
        method,
        url,
        query_params=None,
        headers=None,
        post_params=None,
        body=None,
        _preload_content=True,
        _request_timeout=None,
    ):
        headers = {} if headers is None else headers

        try:
            self.add_client_creds_token_header(headers)
            return super().request(  # type:ignore
                method, url, query_params, headers, post_params, body, _preload_content, _request_timeout
            )
        except Exception as ex:
            if is_api_exception(ex) and ex.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):  # type:ignore
                logger.warning("Access Denied. Token expired? Retrying.", api_exception=str(ex))
                loop = new_event_loop()
                loop.run_until_complete(self.refresh_client_creds_token(force=True))
                self.add_client_creds_token_header(headers)

                return super().request(  # type:ignore
                    method, url, query_params, headers, post_params, body, _preload_content, _request_timeout
                )
            if is_api_exception(ex) and ex.status == HTTPStatus.NOT_FOUND:  # type:ignore
                logger.debug(ex, url=url)  # noqa: G200
                raise
            logger.exception("Could not call API.", client=self.__class__.__name__)
            raise
