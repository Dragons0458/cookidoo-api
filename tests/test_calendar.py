"""Unit tests for cookidoo-api."""

from datetime import datetime
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
    COOKIDOO_TEST_RESPONSE_ADD_CUSTOM_RECIPES_TO_CALENDAR,
    COOKIDOO_TEST_RESPONSE_ADD_RECIPES_TO_CALENDAR,
    COOKIDOO_TEST_RESPONSE_CALENDAR_WEEK,
    COOKIDOO_TEST_RESPONSE_REMOVE_CUSTOM_RECIPE_FROM_CALENDAR,
    COOKIDOO_TEST_RESPONSE_REMOVE_RECIPE_FROM_CALENDAR,
)

load_dotenv()

class TestGetCalendarWeek:
    """Tests for get_calendar_week method."""

    async def test_get_calendar_week(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for get_calendar_week."""

        mocked.get(
            "https://cookidoo.ch/planning/de-CH/api/my-week/2025-03-03",
            payload=COOKIDOO_TEST_RESPONSE_CALENDAR_WEEK,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.calendar.week(
            datetime.fromisoformat("2025-03-03").date()
        )
        assert data
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0].id == "2025-03-04"
        assert data[0].recipes[0].id == "r214846"
        assert data[1].id == "2025-03-05"
        assert data[1].recipes[0].id == "r338888"

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
            "https://cookidoo.ch/planning/de-CH/api/my-week/2025-03-03",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.calendar.week(
                datetime.fromisoformat("2025-03-03").date()
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/planning/de-CH/api/my-week/2025-03-03",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.calendar.week(
                datetime.fromisoformat("2025-03-03").date()
            )

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
            "https://cookidoo.ch/planning/de-CH/api/my-week/2025-03-03",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.calendar.week(
                datetime.fromisoformat("2025-03-03").date()
            )

class TestAddRecipesToCalendar:
    """Tests for add_recipes_to_calendar method."""

    async def test_add_recipes_to_custom_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for add_recipes_to_calendar."""

        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            payload=COOKIDOO_TEST_RESPONSE_ADD_RECIPES_TO_CALENDAR,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.calendar.add_recipes(
            datetime.fromisoformat("2025-03-04").date(), ["r214846"]
        )
        assert data
        assert data.id == "2025-03-04"
        assert data.recipes[0].id == "r214846"

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

        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.calendar.add_recipes(
                datetime.fromisoformat("2025-03-04").date(), ["r214846"]
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.calendar.add_recipes(
                datetime.fromisoformat("2025-03-04").date(), ["r214846"]
            )

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
        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.calendar.add_recipes(
                datetime.fromisoformat("2025-03-04").date(), ["r214846"]
            )

class TestRemoveRecipeFromCalendar:
    """Tests for remove_recipe_from_calendar method."""

    async def test_remove_recipe_from_calendar(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for remove_recipe_from_calendar."""

        mocked.delete(
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-03-04/recipes/r214846",
            payload=COOKIDOO_TEST_RESPONSE_REMOVE_RECIPE_FROM_CALENDAR,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.calendar.remove_recipe(
            datetime.fromisoformat("2025-03-04").date(), "r214846"
        )
        assert data
        assert data.id == "2025-03-04"
        assert data.recipes[0].id == "r214846"

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
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-03-04/recipes/r214846",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.calendar.remove_recipe(
                datetime.fromisoformat("2025-03-04").date(), "r214846"
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.delete(
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-03-04/recipes/r214846",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.calendar.remove_recipe(
                datetime.fromisoformat("2025-03-04").date(), "r214846"
            )

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
        mocked.delete(
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-03-04/recipes/r214846",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.calendar.remove_recipe(
                datetime.fromisoformat("2025-03-04").date(), "r214846"
            )

class TestAddCustomRecipesToCalendar:
    """Tests for add_custom_recipes_to_calendar method."""

    async def test_add_custom_recipes_to_custom_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for add_custom_recipes_to_calendar."""

        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            payload=COOKIDOO_TEST_RESPONSE_ADD_CUSTOM_RECIPES_TO_CALENDAR,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.calendar.add_custom_recipes(
            datetime.fromisoformat("2025-08-11").date(), ["01K2CTJ9Y1BABRG5MXK44CFZS4"]
        )
        assert data
        assert data.id == "2025-08-11"

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

        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.calendar.add_custom_recipes(
                datetime.fromisoformat("2025-08-11").date(),
                ["01K2CTJ9Y1BABRG5MXK44CFZS4"],
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.calendar.add_custom_recipes(
                datetime.fromisoformat("2025-08-11").date(),
                ["01K2CTJ9Y1BABRG5MXK44CFZS4"],
            )

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
        mocked.put(
            "https://cookidoo.ch/planning/de-CH/api/my-day",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.calendar.add_custom_recipes(
                datetime.fromisoformat("2025-08-11").date(),
                ["01K2CTJ9Y1BABRG5MXK44CFZS4"],
            )

class TestRemoveCustomRecipeFromCalendar:
    """Tests for remove_custom_recipe_from_calendar method."""

    async def test_remove_custom_recipe_from_calendar(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for remove_custom_recipe_from_calendar."""

        mocked.delete(
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-08-11/recipes/r214846?recipeSource=CUSTOMER",
            payload=COOKIDOO_TEST_RESPONSE_REMOVE_CUSTOM_RECIPE_FROM_CALENDAR,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.calendar.remove_custom_recipe(
            datetime.fromisoformat("2025-08-11").date(), "r214846"
        )
        assert data
        assert data.id == "2025-08-11"

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
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-08-11/recipes/01K2CTJ9Y1BABRG5MXK44CFZS4?recipeSource=CUSTOMER",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.calendar.remove_custom_recipe(
                datetime.fromisoformat("2025-08-11").date(),
                "01K2CTJ9Y1BABRG5MXK44CFZS4",
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.delete(
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-08-11/recipes/01K2CTJ9Y1BABRG5MXK44CFZS4?recipeSource=CUSTOMER",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.calendar.remove_custom_recipe(
                datetime.fromisoformat("2025-08-11").date(),
                "01K2CTJ9Y1BABRG5MXK44CFZS4",
            )

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
        mocked.delete(
            "https://cookidoo.ch/planning/de-CH/api/my-day/2025-08-11/recipes/01K2CTJ9Y1BABRG5MXK44CFZS4?recipeSource=CUSTOMER",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.calendar.remove_custom_recipe(
                datetime.fromisoformat("2025-08-11").date(),
                "01K2CTJ9Y1BABRG5MXK44CFZS4",
            )
