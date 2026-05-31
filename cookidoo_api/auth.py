"""Cookidoo authentication service."""

from http import HTTPStatus
from http.cookies import SimpleCookie
import json
import logging
from pathlib import Path
import re
import traceback

from aiohttp import ClientError
from yarl import URL

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import CIAM_LOGIN_SRV_URL, LOGIN_PATH, LOGIN_REDIRECT
from cookidoo_api.exceptions import (
    CookidooAuthException,
    CookidooConfigException,
    CookidooParseException,
    CookidooRequestException,
)

_LOGGER = logging.getLogger(__name__)


class CookidooAuthService:
    """CookidooAuth service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo authentication service."""
        self._client = client

    async def login(self) -> None:
        """Perform browser-based OAuth2 login.

        Follows the same redirect chain as the Cookidoo web app:
        1. Initiate login at ``cookidoo.{tld}/profile/{lang}/login``
        2. Follow redirects through OAuth2/PKCE to the CIAM login page
        3. POST credentials to the CIAM login service
        4. Follow callback redirects to capture session cookies

        After login, the session's cookie jar contains the authentication
        cookies and all subsequent API calls are authenticated automatically.

        Raises
        ------
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the login page cannot be parsed.
        CookidooAuthException
            If the login fails due to invalid credentials.

        """
        language = self._client._cfg.localization.language
        login_path = LOGIN_PATH.format(language=language)
        redirect = LOGIN_REDIRECT.format(language=language)
        login_url = URL(
            str(self._client.api_endpoint / login_path) + f"?redirectAfterLogin={redirect}",
            encoded=True,
        )

        try:
            # Step 1: Follow redirect chain to reach the CIAM login page
            async with self._client._session.get(login_url, allow_redirects=True) as resp:
                self._check_login_page_status(resp.status)
                login_html = await resp.text()

            # Step 2: Extract requestId from the login form
            request_id = self._extract_request_id(login_html)

            # Step 3: POST credentials to CIAM login service
            login_data = {
                "requestId": request_id,
                "username": self._client._cfg.email,
                "password": self._client._cfg.password,
            }
            async with self._client._session.post(
                CIAM_LOGIN_SRV_URL,
                data=login_data,
                allow_redirects=True,
            ) as resp:
                _LOGGER.debug(
                    "Login POST completed, final URL: %s (status: %s)",
                    resp.url,
                    resp.status,
                )

            # Step 4: Verify authentication cookies were set
            self._verify_auth_cookies()
            self._client._logged_in = True

        except CookidooAuthException:
            raise
        except CookidooParseException:
            raise
        except TimeoutError as e:
            _LOGGER.debug("Exception: Login failed:\n %s", traceback.format_exc())
            raise CookidooRequestException(
                "Authentication failed due to connection timeout."
            ) from e
        except ClientError as e:
            _LOGGER.debug("Exception: Login failed:\n %s", traceback.format_exc())
            raise CookidooRequestException(
                "Authentication failed due to request exception."
            ) from e

    @staticmethod
    def _check_login_page_status(status: int) -> None:
        """Check login page response status."""
        if status != HTTPStatus.OK:
            raise CookidooAuthException(
                f"Login flow failed: could not reach login page (status {status})."
            )

    @staticmethod
    def _extract_request_id(login_html: str) -> str:
        """Extract requestId from the CIAM login page HTML."""
        match = re.search(
            r'<input[^>]*name=["\']requestId["\'][^>]*value=["\']([^"\']+)["\']',
            login_html,
        ) or re.search(
            r'<input[^>]*value=["\']([0-9a-f-]{36})["\'][^>]*name=["\']requestId["\']',
            login_html,
        )
        if not match:
            raise CookidooParseException(
                "Login flow failed: could not extract requestId from login page."
            )
        return match.group(1)

    def _verify_auth_cookies(self) -> None:
        """Verify that required authentication cookies are present."""
        cookie_names = {c.key for c in self._client._session.cookie_jar}
        required_cookies = {"_oauth2_proxy", "v-authenticated"}
        if not required_cookies.issubset(cookie_names):
            raise CookidooAuthException(
                "Login failed: authentication cookies were not set. "
                "Please check your email and password."
            )

    def save_cookies(self, path: str | Path) -> None:
        """Save session cookies to a file for later reuse.

        Parameters
        ----------
        path
            Path to the file where cookies will be saved.

        """
        cookies: list[dict[str, str]] = []
        for cookie in self._client._session.cookie_jar:
            cookies.append(
                {
                    "key": cookie.key,
                    "value": cookie.value,
                    "domain": cookie["domain"],
                    "path": cookie["path"],
                }
            )
        Path(path).write_text(json.dumps(cookies), encoding="utf-8")

    def load_cookies(self, path: str | Path) -> None:
        """Load session cookies from a file to restore a previous session.

        Parameters
        ----------
        path
            Path to the file containing saved cookies.

        Raises
        ------
        CookidooConfigException
            If the cookie file cannot be read or parsed.

        """
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise CookidooConfigException(f"Cannot load cookies from {path}.") from e

        for entry in data:
            cookie: SimpleCookie = SimpleCookie()
            cookie[entry["key"]] = entry["value"]
            cookie[entry["key"]]["domain"] = entry.get("domain", "")
            cookie[entry["key"]]["path"] = entry.get("path", "/")
            self._client._session.cookie_jar.update_cookies(
                cookie, URL(f"https://{entry.get('domain', '')}")
            )

        # Check if required auth cookies are present
        cookie_names = {c.key for c in self._client._session.cookie_jar}
        required_cookies = {"_oauth2_proxy", "v-authenticated"}
        if required_cookies.issubset(cookie_names):
            self._client._logged_in = True
