"""Unit tests for cookidoo-api."""

from http import HTTPStatus

from aiohttp import ClientError
from aioresponses import aioresponses
from dotenv import load_dotenv
import pytest

from cookidoo_api.cookidoo import Cookidoo
from cookidoo_api.exceptions import (
    CookidooAuthException,
    CookidooParseException,
    CookidooRequestException,
)
from tests.responses import (
    COOKIDOO_TEST_LOGIN_PAGE_HTML,
    COOKIDOO_TEST_RESPONSE_USER_INFO,
)

load_dotenv()

class TestLogin:
    """Tests for login method."""

    async def test_login_success(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test successful login via browser OAuth2 flow."""
        import re

        # Mock the login page (GET follows redirects to CIAM login page)
        mocked.get(
            re.compile(r"https://cookidoo\.ch/profile/de-CH/login.*"),
            status=HTTPStatus.OK,
            body=COOKIDOO_TEST_LOGIN_PAGE_HTML,
        )

        # Mock the CIAM login POST (returns redirect with auth cookies)
        mocked.post(
            "https://ciam.prod.cookidoo.vorwerk-digital.com/login-srv/login",
            status=HTTPStatus.OK,
        )

        # Manually set cookies since aioresponses doesn't handle Set-Cookie
        cookidoo._session.cookie_jar.update_cookies(
            {"_oauth2_proxy": "test-proxy-value", "v-authenticated": "test-auth-value"}
        )

        await cookidoo.auth.login()
        assert cookidoo._logged_in

    async def test_login_page_unreachable(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test login when login page returns error."""
        import re

        mocked.get(
            re.compile(r"https://cookidoo\.ch/profile/de-CH/login.*"),
            status=HTTPStatus.SERVICE_UNAVAILABLE,
        )

        with pytest.raises(CookidooAuthException, match="could not reach login page"):
            await cookidoo.auth.login()

    async def test_login_page_parse_error(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test login when requestId cannot be extracted."""
        import re

        mocked.get(
            re.compile(r"https://cookidoo\.ch/profile/de-CH/login.*"),
            status=HTTPStatus.OK,
            body="<html><body>No form here</body></html>",
        )

        with pytest.raises(CookidooParseException, match="could not extract requestId"):
            await cookidoo.auth.login()

    async def test_login_invalid_credentials(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test login with invalid credentials (no auth cookies set)."""
        import re

        mocked.get(
            re.compile(r"https://cookidoo\.ch/profile/de-CH/login.*"),
            status=HTTPStatus.OK,
            body=COOKIDOO_TEST_LOGIN_PAGE_HTML,
        )
        mocked.post(
            "https://ciam.prod.cookidoo.vorwerk-digital.com/login-srv/login",
            status=HTTPStatus.OK,
        )

        with pytest.raises(
            CookidooAuthException, match="authentication cookies were not set"
        ):
            await cookidoo.auth.login()

    @pytest.mark.parametrize(
        "exception",
        [
            TimeoutError,
            ClientError,
        ],
    )
    async def test_request_exceptions(
        self, mocked: aioresponses, cookidoo: Cookidoo, exception: Exception
    ) -> None:
        """Test exceptions."""
        import re

        mocked.get(
            re.compile(r"https://cookidoo\.ch/profile/de-CH/login.*"),
            exception=exception,
        )
        with pytest.raises(CookidooRequestException):
            await cookidoo.auth.login()

class TestCookiePersistence:
    """Tests for cookie save/load methods."""

    async def test_save_and_load_cookies(
        self, cookidoo: Cookidoo, tmp_path: object
    ) -> None:
        """Test saving and loading cookies."""
        import pathlib

        cookie_file = pathlib.Path(str(tmp_path)) / "cookies.json"

        # Set some cookies on the session
        cookidoo._session.cookie_jar.update_cookies(
            {"_oauth2_proxy": "proxy-val", "v-authenticated": "auth-val"}
        )

        # Save
        cookidoo.auth.save_cookies(cookie_file)
        assert cookie_file.exists()

        # Load into a fresh Cookidoo instance on same session
        # (clear cookies first)
        cookidoo._session.cookie_jar.clear()
        assert not cookidoo._logged_in or True  # reset
        cookidoo._logged_in = False

        cookidoo.auth.load_cookies(cookie_file)
        assert cookidoo._logged_in

        cookie_names = {c.key for c in cookidoo._session.cookie_jar}
        assert "_oauth2_proxy" in cookie_names
        assert "v-authenticated" in cookie_names

    async def test_load_cookies_missing_file(self, cookidoo: Cookidoo) -> None:
        """Test loading cookies from nonexistent file."""
        from cookidoo_api.exceptions import CookidooConfigException

        with pytest.raises(CookidooConfigException, match="Cannot load cookies"):
            cookidoo.auth.load_cookies("/nonexistent/path/cookies.json")

    async def test_load_cookies_without_auth_cookies(
        self, cookidoo: Cookidoo, tmp_path: object
    ) -> None:
        """Test that loading cookies without required auth cookies does not set logged_in."""
        import json
        import pathlib

        cookie_file = pathlib.Path(str(tmp_path)) / "cookies.json"
        cookie_file.write_text(
            json.dumps(
                [{"key": "some_other", "value": "val", "domain": "", "path": "/"}]
            )
        )
        cookidoo._logged_in = False
        cookidoo.auth.load_cookies(cookie_file)
        assert not cookidoo._logged_in

    async def test_corrupted_cookies_recovery(
        self, mocked: aioresponses, cookidoo: Cookidoo, tmp_path: object
    ) -> None:
        """Test recovery flow: load expired/corrupted cookies, API fails, re-login succeeds."""
        import pathlib
        import re

        cookie_file = pathlib.Path(str(tmp_path)) / "cookies.json"

        # Set corrupted/expired auth cookies
        cookidoo._session.cookie_jar.update_cookies(
            {"_oauth2_proxy": "corrupted-value", "v-authenticated": "expired"}
        )
        cookidoo.auth.save_cookies(cookie_file)

        # Clear and reload the corrupted cookies
        cookidoo._session.cookie_jar.clear()
        cookidoo._logged_in = False
        cookidoo.auth.load_cookies(cookie_file)
        assert cookidoo._logged_in  # Cookies are present, so flag is set

        # API call fails with 401 because cookies are invalid
        mocked.get(
            "https://cookidoo.ch/community/profile",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error": "Unauthorized", "error_description": "Token expired"},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.account.get_user_info()

        # Recovery: re-login
        mocked.get(
            re.compile(r"https://cookidoo\.ch/profile/de-CH/login.*"),
            status=HTTPStatus.OK,
            body=COOKIDOO_TEST_LOGIN_PAGE_HTML,
        )
        mocked.post(
            "https://ciam.prod.cookidoo.vorwerk-digital.com/login-srv/login",
            status=HTTPStatus.OK,
        )
        cookidoo._session.cookie_jar.update_cookies(
            {
                "_oauth2_proxy": "fresh-proxy-value",
                "v-authenticated": "fresh-auth-value",
            }
        )
        await cookidoo.auth.login()
        assert cookidoo._logged_in

        # API call now succeeds
        mocked.get(
            "https://cookidoo.ch/community/profile",
            payload=COOKIDOO_TEST_RESPONSE_USER_INFO,
            status=HTTPStatus.OK,
        )
        data = await cookidoo.account.get_user_info()
        assert data.username == COOKIDOO_TEST_RESPONSE_USER_INFO["userInfo"]["username"]  # type: ignore[index]

        # Save fresh cookies for next run
        cookidoo.auth.save_cookies(cookie_file)
