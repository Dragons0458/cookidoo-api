"""Shared Cookidoo client HTTP helpers."""

from collections.abc import Callable, Mapping, Sequence
from http import HTTPStatus
from json import JSONDecodeError
import logging
import traceback
from typing import TYPE_CHECKING, TypeVar

from aiohttp import ClientError
from yarl import URL

from cookidoo_api.exceptions import (
    CookidooAuthException,
    CookidooParseException,
    CookidooRequestException,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession

    from cookidoo_api.types import CookidooConfig

_LOGGER = logging.getLogger(__name__)
_T = TypeVar("_T")


class CookidooClientBase:
    """Shared state and request helpers for Cookidoo services."""

    _session: "ClientSession"
    _cfg: "CookidooConfig"
    _api_headers: dict[str, str]
    _logged_in: bool

    @property
    def api_endpoint(self) -> URL:
        """Get the API endpoint."""
        raise NotImplementedError

    @staticmethod
    def _raise_auth_exception(operation: str) -> None:
        """Raise the standard auth exception for request helpers."""
        raise CookidooAuthException(
            f"{operation.capitalize()} failed due to authorization failure, "
            "the authorization token is invalid or expired."
        )

    @staticmethod
    def _ensure_mapping(result: object | None, operation: str) -> Mapping[str, object]:
        """Return a mapping response or raise the standard parse exception."""
        if not isinstance(result, Mapping):
            raise CookidooParseException(
                f"{operation.capitalize()} failed during parsing of request response."
            )
        return result

    @staticmethod
    def _ensure_sequence(result: object | None, operation: str) -> Sequence[object]:
        """Return a sequence response or raise the standard parse exception."""
        if isinstance(result, str) or not isinstance(result, Sequence):
            raise CookidooParseException(
                f"{operation.capitalize()} failed during parsing of request response."
            )
        return result

    @staticmethod
    def _parse_result(operation: str, parser: Callable[[], _T]) -> _T:
        """Convert a validated JSON response into public types."""
        try:
            return parser()
        except (KeyError, TypeError, ValueError) as e:
            raise CookidooParseException(
                f"{operation.capitalize()} failed during parsing of request response."
            ) from e

    async def _request_json(
        self,
        method: str,
        url: URL,
        operation: str,
        *,
        params: dict[str, str] | None = None,
        json: object | None = None,
        headers: dict[str, str] | None = None,
        accepted_statuses: tuple[HTTPStatus, ...] = (
            HTTPStatus.OK,
            HTTPStatus.NO_CONTENT,
        ),
        parse_response: bool = True,
    ) -> object | None:
        """Execute an HTTP request and parse its JSON response."""
        merged_headers = {**self._api_headers, **(headers or {})}

        try:
            async with self._session.request(
                method, url, headers=merged_headers, json=json, params=params
            ) as r:
                _LOGGER.debug(
                    "Response from %s [%s]: %s", url, r.status, await r.text()
                )

                if r.status == HTTPStatus.UNAUTHORIZED:
                    try:
                        errmsg = await r.json()
                    except (JSONDecodeError, ClientError):
                        _LOGGER.debug(
                            "Exception: Cannot parse request response:\n %s",
                            traceback.format_exc(),
                        )
                    else:
                        _LOGGER.debug(
                            "Exception: Cannot %s: %s",
                            operation,
                            errmsg.get("error_description", ""),
                        )
                    self._raise_auth_exception(operation)

                if r.status not in accepted_statuses:
                    r.raise_for_status()

                if r.status == HTTPStatus.NO_CONTENT:
                    return None
                if not parse_response:
                    return None
                try:
                    result: object = await r.json()
                except (JSONDecodeError, KeyError) as e:
                    _LOGGER.debug(
                        "Exception: Cannot parse %s response:\n%s",
                        operation,
                        traceback.format_exc(),
                    )
                    raise CookidooParseException(
                        f"{operation.capitalize()} failed during parsing of request response."
                    ) from e
                else:
                    return result

        except (
            CookidooAuthException,
            CookidooRequestException,
            CookidooParseException,
        ):
            raise
        except TimeoutError as e:
            _LOGGER.debug(
                "Exception: Cannot %s:\n%s", operation, traceback.format_exc()
            )
            raise CookidooRequestException(
                f"{operation.capitalize()} failed due to connection timeout."
            ) from e
        except ClientError as e:
            _LOGGER.debug(
                "Exception: Cannot %s:\n%s", operation, traceback.format_exc()
            )
            raise CookidooRequestException(
                f"{operation.capitalize()} failed due to request exception."
            ) from e

