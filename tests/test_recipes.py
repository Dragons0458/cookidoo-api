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
from cookidoo_api.types import CookidooSearchResult, ThermomixMachineType
from tests.responses import (
    COOKIDOO_TEST_RESPONSE_GET_RECIPE_DETAILS,
    COOKIDOO_TEST_RESPONSE_SEARCH_RECIPES,
)

load_dotenv()

class TestGetRecipeDetails:
    """Tests for get_recipe_details method."""

    async def test_get_recipe_details(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for get_recipe_details."""

        mocked.get(
            "https://cookidoo.ch/recipes/recipe/de-CH/r907015",
            payload=COOKIDOO_TEST_RESPONSE_GET_RECIPE_DETAILS,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.recipes.get_details("r907015")
        assert data
        assert isinstance(data, object)
        assert data.id == "r907015"
        assert data.name == "Kokos Pralinen"
        assert isinstance(data.categories, list)
        assert isinstance(data.collections, list)
        assert isinstance(data.ingredients, list)
        assert isinstance(data.notes, list)
        assert isinstance(data.utensils, list)
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
            "https://cookidoo.ch/recipes/recipe/de-CH/r907015",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.recipes.get_details("r907015")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/recipes/recipe/de-CH/r907015",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.recipes.get_details("r907015")

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
            "https://cookidoo.ch/recipes/recipe/de-CH/r907015",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.recipes.get_details("r907015")

class TestSearchRecipes:
    """Tests for search_recipes method."""

    async def test_search_recipes(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for search_recipes."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            payload=COOKIDOO_TEST_RESPONSE_SEARCH_RECIPES,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.recipes.search("chicken")
        assert isinstance(data, CookidooSearchResult)
        assert data.total == 2
        assert len(data.recipes) == 2
        assert data.recipes[0].id == "r123456"
        assert data.recipes[0].name == "Chicken Soup"
        assert data.recipes[0].thumbnail == (
            "https://assets.tmecosys.com/image/upload/"
            "t_web_shared_recipe_221x240/img/recipe/ras/Assets/"
            "a1b2c3d4-1111-2222-3333-444455556666/Derivates/"
            "abcdef01-2345-6789-abcd-ef0123456789.jpg"
        )
        assert data.recipes[0].image == (
            "https://assets.tmecosys.com/image/upload/"
            "t_web_rdp_recipe_584x480_1_5x/img/recipe/ras/Assets/"
            "a1b2c3d4-1111-2222-3333-444455556666/Derivates/"
            "abcdef01-2345-6789-abcd-ef0123456789.jpg"
        )
        assert data.recipes[0].url == (
            "https://cookidoo.ch/recipes/recipe/de-CH/r123456"
        )
        assert data.recipes[1].id == "r654321"
        assert data.recipes[1].name == "Chicken Salad"
        assert data.recipes[1].thumbnail == (
            "https://assets.tmecosys.com/image/upload/"
            "t_web_shared_recipe_221x240/img/recipe/ras/Assets/"
            "f1e2d3c4-9999-8888-7777-666655554444/Derivates/"
            "98765432-10fe-dcba-9876-543210fedcba.jpg"
        )
        assert data.recipes[1].image == (
            "https://assets.tmecosys.com/image/upload/"
            "t_web_rdp_recipe_584x480_1_5x/img/recipe/ras/Assets/"
            "f1e2d3c4-9999-8888-7777-666655554444/Derivates/"
            "98765432-10fe-dcba-9876-543210fedcba.jpg"
        )
        assert data.recipes[1].url == (
            "https://cookidoo.ch/recipes/recipe/de-CH/r654321"
        )

    async def test_search_recipes_with_options(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes with filters and list parameters."""
        accessories = [
            "includingFriend",
            "includingBladeCover",
            "includingBladeCoverWithPeeler",
            "includingCutter",
            "includingSensor",
        ]
        categories = [
            "VrkNavCategory-RPF-001",
            "VrkNavCategory-RPF-002",
            "VrkNavCategory-RPF-003",
        ]
        url = (
            "https://cookidoo.ch/search/es?"
            "query=chicken"
            "&accessories=includingFriend,includingBladeCover,includingBladeCoverWithPeeler,includingCutter,includingSensor"
            "&languages=en,es"
            "&categories=VrkNavCategory-RPF-001,VrkNavCategory-RPF-002,VrkNavCategory-RPF-003"
            "&countries=ar,es"
            "&ingredients=sal,aceite%20de%20oliva"
            "&excludeIngredients=polvo%20de%20hornear"
            "&tags=De%20diario"
            "&ratings=5,4"
            "&difficulty=easy"
            "&preparationTime=900"
            "&totalTime=1200"
            "&portions=2"
            "&page=1"
            "&pageSize=10"
            "&tmv=TM7,TM6,TM5,TM31"
        )
        mocked.get(
            url,
            payload=COOKIDOO_TEST_RESPONSE_SEARCH_RECIPES,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.recipes.search(
            "chicken",
            locale="es",
            accessories=accessories,
            languages=["en", "es"],
            categories=categories,
            countries=["ar", "es"],
            ingredients=["sal", "aceite de oliva"],
            exclude_ingredients=["polvo de hornear"],
            tags=["De diario"],
            ratings=["5", "4"],
            difficulty="easy",
            preparation_time=900,
            total_time=1200,
            portions=2,
            page=1,
            page_size=10,
            tmv=["TM7", "TM6", "TM5", "TM31"],
        )
        assert isinstance(data, CookidooSearchResult)
        assert len(data.recipes) == 2
        assert data.total == 2

    @pytest.mark.parametrize(
        "exception",
        [
            TimeoutError,
            ClientError,
        ],
    )
    async def test_search_recipes_request_exception(
        self, mocked: aioresponses, cookidoo: Cookidoo, exception: Exception
    ) -> None:
        """Test search_recipes request exceptions."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.recipes.search("chicken")

    async def test_search_recipes_unauthorized(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.recipes.search("chicken")

    async def test_search_recipes_unauthorized_non_json_body(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes 401 with non-JSON body still raises CookidooAuthException."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            status=HTTPStatus.UNAUTHORIZED,
            body="not json",
            content_type="text/plain",
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.recipes.search("chicken")

    async def test_search_recipes_parse_exception(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes raises CookidooParseException when response is not valid JSON."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            status=HTTPStatus.OK,
            body="not valid json",
            content_type="application/json",
        )
        with pytest.raises(CookidooParseException):
            await cookidoo.recipes.search("chicken")

    async def test_search_recipes_no_content(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes when API returns 204 No Content."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            status=HTTPStatus.NO_CONTENT,
        )

        data = await cookidoo.recipes.search("chicken")
        assert isinstance(data, CookidooSearchResult)
        assert data.recipes == []
        assert data.total == 0

    async def test_search_recipes_with_string_params(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes with string (non-list) filter params."""
        url = (
            "https://cookidoo.ch/search/de?"
            "query=pasta&accessories=includingFriend&difficulty=easy"
        )
        mocked.get(
            url,
            payload=COOKIDOO_TEST_RESPONSE_SEARCH_RECIPES,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.recipes.search(
            "pasta",
            accessories="includingFriend",
            difficulty="easy",
        )
        assert isinstance(data, CookidooSearchResult)
        assert data.total == 2

    async def test_search_recipes_with_tmv_single_enum(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes with single ThermomixMachineType (not list)."""
        url = "https://cookidoo.ch/search/de?query=soup&tmv=TM7"
        mocked.get(
            url,
            payload=COOKIDOO_TEST_RESPONSE_SEARCH_RECIPES,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.recipes.search("soup", tmv=ThermomixMachineType.TM7)
        assert isinstance(data, CookidooSearchResult)
        assert data.total == 2

    async def test_search_recipes_without_query(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes with optional query omitted (params without query)."""
        mocked.get(
            "https://cookidoo.ch/search/de",
            payload=COOKIDOO_TEST_RESPONSE_SEARCH_RECIPES,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.recipes.search()
        assert isinstance(data, CookidooSearchResult)
        assert len(data.recipes) == 2
        assert data.total == 2

    async def test_search_recipes_unexpected_status(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes raises CookidooRequestException on unexpected status."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        with pytest.raises(CookidooRequestException):
            await cookidoo.recipes.search("chicken")

    async def test_search_recipes_non_dict_response(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test search_recipes raises CookidooParseException when response is not a dict."""
        mocked.get(
            "https://cookidoo.ch/search/de?query=chicken",
            payload=["not", "a", "dict"],
            status=HTTPStatus.OK,
        )
        with pytest.raises(CookidooParseException):
            await cookidoo.recipes.search("chicken")
