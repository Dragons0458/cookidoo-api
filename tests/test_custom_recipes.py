"""Unit tests for cookidoo-api."""

from http import HTTPStatus

from aiohttp import ClientError
from aioresponses import aioresponses
from dotenv import load_dotenv
import pytest

from cookidoo_api.cookidoo import Cookidoo
from cookidoo_api.exceptions import (
    CookidooAuthException,
    CookidooException,
    CookidooParseException,
    CookidooRequestException,
)
from tests.responses import (
    COOKIDOO_TEST_RESPONSE_ADD_CUSTOM_RECIPE,
    COOKIDOO_TEST_RESPONSE_GET_CUSTOM_RECIPE,
)

load_dotenv()

class TestGetCustomRecipe:
    """Tests for get_custom_recipe method."""

    async def test_get_custom_recipe(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for get_custom_recipe."""

        mocked.get(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CVHD1DXG1PVETNVV3JPKWW",
            payload=COOKIDOO_TEST_RESPONSE_GET_CUSTOM_RECIPE,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.custom_recipes.get("01K2CVHD1DXG1PVETNVV3JPKWW")
        assert data
        assert isinstance(data, object)
        assert data.id == "01K2CVHD1DXG1PVETNVV3JPKWW"
        assert data.name == "Vongole alla marinara"
        assert isinstance(data.instructions, list)
        assert isinstance(data.ingredients, list)
        assert isinstance(data.tools, list)
        assert isinstance(data.active_time, int)
        assert isinstance(data.total_time, int)
        assert isinstance(data.serving_size, int)

    @pytest.mark.parametrize(
        "exception",
        [
            TimeoutError,
            ClientError,
        ],
    )
    async def test_request_exception(
        self, mocked: aioresponses, cookidoo: Cookidoo, exception: Exception
    ) -> None:
        """Test request exceptions."""

        mocked.get(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CVHD1DXG1PVETNVV3JPKWW",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.custom_recipes.get("01K2CVHD1DXG1PVETNVV3JPKWW")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CVHD1DXG1PVETNVV3JPKWW",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.custom_recipes.get("01K2CVHD1DXG1PVETNVV3JPKWW")

    @pytest.mark.parametrize(
        ("status", "exception"),
        [
            (HTTPStatus.OK, CookidooParseException),
            (HTTPStatus.UNAUTHORIZED, CookidooAuthException),
        ],
    )
    async def test_parse_exception(
        self,
        mocked: aioresponses,
        cookidoo: Cookidoo,
        status: HTTPStatus,
        exception: type[CookidooException],
    ) -> None:
        """Test parse exceptions."""
        mocked.get(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CVHD1DXG1PVETNVV3JPKWW",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.custom_recipes.get("01K2CVHD1DXG1PVETNVV3JPKWW")

class TestAddCustomRecipe:
    """Tests for add_custom_recipe method."""

    async def test_add_custom_recipe(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for add_custom_recipe."""

        mocked.post(
            "https://cookidoo.ch/created-recipes/de-CH",
            payload=COOKIDOO_TEST_RESPONSE_ADD_CUSTOM_RECIPE,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.custom_recipes.add_from("r907015", 4)
        assert data
        assert data.id == "01K2CTJ9Y1BABRG5MXK44CFZS4"
        assert data.name == "Vongole alla marinara"

    @pytest.mark.parametrize(
        "exception",
        [
            TimeoutError,
            ClientError,
        ],
    )
    async def test_request_exception(
        self, mocked: aioresponses, cookidoo: Cookidoo, exception: Exception
    ) -> None:
        """Test request exceptions."""

        mocked.post(
            "https://cookidoo.ch/created-recipes/de-CH",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.custom_recipes.add_from("r907015", 4)

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.post(
            "https://cookidoo.ch/created-recipes/de-CH",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.custom_recipes.add_from("r907015", 4)

    @pytest.mark.parametrize(
        ("status", "exception"),
        [
            (HTTPStatus.OK, CookidooParseException),
            (HTTPStatus.UNAUTHORIZED, CookidooAuthException),
        ],
    )
    async def test_parse_exception(
        self,
        mocked: aioresponses,
        cookidoo: Cookidoo,
        status: HTTPStatus,
        exception: type[CookidooException],
    ) -> None:
        """Test parse exceptions."""
        mocked.post(
            "https://cookidoo.ch/created-recipes/de-CH",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.custom_recipes.add_from("r907015", 4)

class TestRemoveCustomRecipe:
    """Tests for remove_custom_recipe method."""

    async def test_remove_custom_recipe(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for remove_custom_recipe."""

        mocked.delete(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CTJ9Y1BABRG5MXK44CFZS4",
            payload=None,
            status=HTTPStatus.OK,
        )

        await cookidoo.custom_recipes.remove("01K2CTJ9Y1BABRG5MXK44CFZS4")

    @pytest.mark.parametrize(
        "exception",
        [
            TimeoutError,
            ClientError,
        ],
    )
    async def test_request_exception(
        self, mocked: aioresponses, cookidoo: Cookidoo, exception: Exception
    ) -> None:
        """Test request exceptions."""

        mocked.delete(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CTJ9Y1BABRG5MXK44CFZS4",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.custom_recipes.remove("01K2CTJ9Y1BABRG5MXK44CFZS4")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.delete(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CTJ9Y1BABRG5MXK44CFZS4",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.custom_recipes.remove("01K2CTJ9Y1BABRG5MXK44CFZS4")

    @pytest.mark.parametrize(
        ("status", "exception"),
        [
            # (HTTPStatus.OK, CookidooParseException), # There is nothing to parse
            (HTTPStatus.UNAUTHORIZED, CookidooAuthException),
        ],
    )
    async def test_parse_exception(
        self,
        mocked: aioresponses,
        cookidoo: Cookidoo,
        status: HTTPStatus,
        exception: type[CookidooException],
    ) -> None:
        """Test parse exceptions."""
        mocked.delete(
            "https://cookidoo.ch/created-recipes/de-CH/01K2CTJ9Y1BABRG5MXK44CFZS4",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.custom_recipes.remove("01K2CTJ9Y1BABRG5MXK44CFZS4")
