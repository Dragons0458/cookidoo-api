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
    COOKIDOO_TEST_RESPONSE_ADD_CUSTOM_COLLECTION,
    COOKIDOO_TEST_RESPONSE_ADD_MANAGED_COLLECTION,
    COOKIDOO_TEST_RESPONSE_ADD_RECIPES_TO_CUSTOM_COLLECTION,
    COOKIDOO_TEST_RESPONSE_GET_CUSTOM_COLLECTIONS,
    COOKIDOO_TEST_RESPONSE_GET_MANAGED_COLLECTIONS,
    COOKIDOO_TEST_RESPONSE_REMOVE_RECIPE_FROM_CUSTOM_COLLECTION,
)

load_dotenv()

class TestCountManagedLists:
    """Tests for count_managed_lists method."""

    async def test_count_managed_lists(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for count_managed_lists."""

        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            payload=COOKIDOO_TEST_RESPONSE_GET_MANAGED_COLLECTIONS,
            status=HTTPStatus.OK,
        )

        count_recipes, count_pages = await cookidoo.collections.managed.count()
        assert count_recipes == 1
        assert count_pages == 1

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.managed.count()

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.managed.count()

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.managed.count()

class TestGetManagedLists:
    """Tests for get_managed_lists method."""

    async def test_get_managed_lists(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for get_managed_lists."""

        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/managed-list?page=0",
            payload=COOKIDOO_TEST_RESPONSE_GET_MANAGED_COLLECTIONS,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.collections.managed.list()
        assert data
        assert isinstance(data, list)
        assert len(data) == 1

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list?page=0",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.managed.list()

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/managed-list?page=0",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.managed.list()

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list?page=0",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.managed.list()

class TestAddManagedCollection:
    """Tests for add_managed_collection method."""

    async def test_add_managed_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for add_managed_collection."""

        mocked.post(
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            payload=COOKIDOO_TEST_RESPONSE_ADD_MANAGED_COLLECTION,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.collections.managed.add("col500561")
        assert data
        assert data.id == "col500561"

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.managed.add("col500561")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.post(
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.managed.add("col500561")

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.managed.add("col500561")

class TestRemoveManagedCollection:
    """Tests for remove_managed_collection method."""

    async def test_remove_managed_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for remove_managed_collection."""

        mocked.delete(
            "https://cookidoo.ch/organize/de-CH/api/managed-list/col500561",
            payload=None,
            status=HTTPStatus.OK,
        )

        await cookidoo.collections.managed.remove("col500561")

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list/col500561",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.managed.remove("col500561")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.delete(
            "https://cookidoo.ch/organize/de-CH/api/managed-list/col500561",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.managed.remove("col500561")

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
            "https://cookidoo.ch/organize/de-CH/api/managed-list/col500561",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.managed.remove("col500561")

class TestCountCustomLists:
    """Tests for count_custom_lists method."""

    async def test_count_custom_lists(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for count_custom_lists."""

        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            payload=COOKIDOO_TEST_RESPONSE_GET_CUSTOM_COLLECTIONS,
            status=HTTPStatus.OK,
        )

        count_recipes, count_pages = await cookidoo.collections.custom.count()
        assert count_recipes == 1
        assert count_pages == 1

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.custom.count()

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.custom.count()

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.custom.count()

class TestGetCustomLists:
    """Tests for get_custom_lists method."""

    async def test_get_custom_lists(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for get_custom_lists."""

        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/custom-list?page=0",
            payload=COOKIDOO_TEST_RESPONSE_GET_CUSTOM_COLLECTIONS,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.collections.custom.list()
        assert data
        assert isinstance(data, list)
        assert len(data) == 1

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list?page=0",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.custom.list()

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.get(
            "https://cookidoo.ch/organize/de-CH/api/custom-list?page=0",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.custom.list()

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list?page=0",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.custom.list()

class TestAddCustomCollection:
    """Tests for add_custom_collection method."""

    async def test_add_custom_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for add_custom_collection."""

        mocked.post(
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            payload=COOKIDOO_TEST_RESPONSE_ADD_CUSTOM_COLLECTION,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.collections.custom.add("Testliste")
        assert data
        assert data.id == "01JC1SRPRSW0SHE0AK8GCASABX"
        assert data.name == "Testliste"

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.custom.add("TEST_COLLECTION")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.post(
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.custom.add("TEST_COLLECTION")

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.custom.add("TEST_COLLECTION")

class TestRemoveCustomCollection:
    """Tests for remove_custom_collection method."""

    async def test_remove_custom_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for remove_custom_collection."""

        mocked.delete(
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            payload=None,
            status=HTTPStatus.OK,
        )

        await cookidoo.collections.custom.remove("01JC1SRPRSW0SHE0AK8GCASABX")

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.custom.remove("01JC1SRPRSW0SHE0AK8GCASABX")

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.delete(
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.custom.remove("01JC1SRPRSW0SHE0AK8GCASABX")

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.custom.remove("01JC1SRPRSW0SHE0AK8GCASABX")

class TestAddRecipesToCustomCollection:
    """Tests for add_recipes_to_custom_collection method."""

    async def test_add_recipes_to_custom_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for add_recipes_to_custom_collection."""

        mocked.put(
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            payload=COOKIDOO_TEST_RESPONSE_ADD_RECIPES_TO_CUSTOM_COLLECTION,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.collections.custom.add_recipes(
            "01JC1SRPRSW0SHE0AK8GCASABX", ["r907015"]
        )
        assert data
        assert data.id == "01JC1SRPRSW0SHE0AK8GCASABX"
        assert data.chapters[0].recipes[0].id == "r907015"

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.custom.add_recipes(
                "01JC1SRPRSW0SHE0AK8GCASABX", ["r907015"]
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.put(
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.custom.add_recipes(
                "01JC1SRPRSW0SHE0AK8GCASABX", ["r907015"]
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
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.custom.add_recipes(
                "01JC1SRPRSW0SHE0AK8GCASABX", ["r907015"]
            )

class TestRemoveRecipeFromCustomCollection:
    """Tests for remove_recipe_from_custom_collection method."""

    async def test_remove_recipe_from_custom_collection(
        self, mocked: aioresponses, cookidoo: Cookidoo
    ) -> None:
        """Test for remove_recipe_from_custom_collection."""

        mocked.delete(
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX/recipes/r907015",
            payload=COOKIDOO_TEST_RESPONSE_REMOVE_RECIPE_FROM_CUSTOM_COLLECTION,
            status=HTTPStatus.OK,
        )

        data = await cookidoo.collections.custom.remove_recipe(
            "01JC1SRPRSW0SHE0AK8GCASABX", "r907015"
        )
        assert data
        assert data.id == "01JC1SRPRSW0SHE0AK8GCASABX"
        assert len(data.chapters[0].recipes) == 0

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
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX/recipes/r907015",
            exception=exception,
        )

        with pytest.raises(CookidooRequestException):
            await cookidoo.collections.custom.remove_recipe(
                "01JC1SRPRSW0SHE0AK8GCASABX", "r907015"
            )

    async def test_unauthorized(self, mocked: aioresponses, cookidoo: Cookidoo) -> None:
        """Test unauthorized exception."""
        mocked.delete(
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX/recipes/r907015",
            status=HTTPStatus.UNAUTHORIZED,
            payload={"error_description": ""},
        )
        with pytest.raises(CookidooAuthException):
            await cookidoo.collections.custom.remove_recipe(
                "01JC1SRPRSW0SHE0AK8GCASABX", "r907015"
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
            "https://cookidoo.ch/organize/de-CH/api/custom-list/01JC1SRPRSW0SHE0AK8GCASABX/recipes/r907015",
            status=status,
            body="not json",
            content_type="application/json",
        )

        with pytest.raises(exception):
            await cookidoo.collections.custom.remove_recipe(
                "01JC1SRPRSW0SHE0AK8GCASABX", "r907015"
            )
