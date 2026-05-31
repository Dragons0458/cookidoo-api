"""Cookidoo collection services."""

from __future__ import annotations

import builtins
from collections.abc import Mapping, Sequence
from typing import Any, cast

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import (
    ADD_CUSTOM_COLLECTION_PATH,
    ADD_MANAGED_COLLECTION_PATH,
    ADD_RECIPES_TO_CUSTOM_COLLECTION_PATH,
    CUSTOM_COLLECTIONS_PATH,
    CUSTOM_COLLECTIONS_PATH_ACCEPT,
    MANAGED_COLLECTIONS_PATH,
    MANAGED_COLLECTIONS_PATH_ACCEPT,
    REMOVE_CUSTOM_COLLECTION_PATH,
    REMOVE_MANAGED_COLLECTION_PATH,
    REMOVE_RECIPE_FROM_CUSTOM_COLLECTION_PATH,
)
from cookidoo_api.helpers import cookidoo_collection_from_json
from cookidoo_api.raw_types import CustomCollectionJSON, ManagedCollectionJSON
from cookidoo_api.types import CookidooCollection


class CookidooManagedCollectionsService:
    """CookidooManagedCollections service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo managed collections service."""
        self._client = client

    async def count(self) -> tuple[int, int]:
        """Get managed collections.

        Returns
        -------
        tuple[int, int]
            The number of managed collections and the number of pages

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / MANAGED_COLLECTIONS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "get",
                url,
                "loading managed collections",
                headers={"ACCEPT": MANAGED_COLLECTIONS_PATH_ACCEPT},
            ),
            "loading managed collections",
        )
        return self._client._parse_result(
            "loading managed collections",
            lambda: (
                int(
                    cast(
                        Any, cast(Mapping[str, object], result["page"])["totalElements"]
                    )
                ),
                int(
                    cast(Any, cast(Mapping[str, object], result["page"])["totalPages"])
                ),
            ),
        )

    async def list(self, page: int = 0) -> builtins.list[CookidooCollection]:
        """Get managed collections.

        Parameters
        ----------
        page
            The page of the managed collections

        Returns
        -------
        list[CookidooCollection]
            The list of the managed collections

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / MANAGED_COLLECTIONS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "get",
                url,
                "loading managed collections",
                params={"page": str(page)},
                headers={"ACCEPT": MANAGED_COLLECTIONS_PATH_ACCEPT},
            ),
            "loading managed collections",
        )
        return self._client._parse_result(
            "loading managed collections",
            lambda: [
                cookidoo_collection_from_json(cast(ManagedCollectionJSON, item))
                for item in cast(Sequence[object], result["managedlists"])
            ],
        )

    async def add(
        self,
        managed_collection_id: str,
    ) -> CookidooCollection:
        """Add managed collections.

        Parameters
        ----------
        managed_collection_id
            The managed collection id to add

        Returns
        -------
        CookidooCollection
            The added managed collection

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"collectionId": managed_collection_id}
        url = self._client.api_endpoint / ADD_MANAGED_COLLECTION_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post",
                url,
                "add managed collection",
                json=json_data,
                headers={"ACCEPT": MANAGED_COLLECTIONS_PATH_ACCEPT},
            ),
            "add managed collection",
        )
        return self._client._parse_result(
            "loading added managed collection",
            lambda: cookidoo_collection_from_json(
                cast(ManagedCollectionJSON, result["content"])
            ),
        )

    async def remove(
        self,
        managed_collection_id: str,
    ) -> None:
        """Remove managed collection.

        Parameters
        ----------
        managed_collection_id
            The managed collection id to remove

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / REMOVE_MANAGED_COLLECTION_PATH.format(
            **self._client._cfg.localization.__dict__, id=managed_collection_id
        )
        await self._client._request_json(
            "delete",
            url,
            "remove managed collection",
            headers={"ACCEPT": MANAGED_COLLECTIONS_PATH_ACCEPT},
            parse_response=False,
        )


class CookidooCustomCollectionsService:
    """CookidooCustomCollections service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo custom collections service."""
        self._client = client

    async def count(self) -> tuple[int, int]:
        """Get custom collections.

        Returns
        -------
        tuple[int, int]
            The number of custom collections and the number of pages

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / CUSTOM_COLLECTIONS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "get",
                url,
                "loading custom collections",
                headers={"ACCEPT": CUSTOM_COLLECTIONS_PATH_ACCEPT},
            ),
            "loading custom collections",
        )
        return self._client._parse_result(
            "loading custom collections",
            lambda: (
                int(
                    cast(
                        Any, cast(Mapping[str, object], result["page"])["totalElements"]
                    )
                ),
                int(
                    cast(Any, cast(Mapping[str, object], result["page"])["totalPages"])
                ),
            ),
        )

    async def list(self, page: int = 0) -> builtins.list[CookidooCollection]:
        """Get custom collections.

        Parameters
        ----------
        page
            The page of the custom collections

        Returns
        -------
        list[CookidooCollection]
            The list of the custom collections

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / CUSTOM_COLLECTIONS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "get",
                url,
                "loading custom collections",
                params={"page": str(page)},
                headers={"ACCEPT": CUSTOM_COLLECTIONS_PATH_ACCEPT},
            ),
            "loading custom collections",
        )
        return self._client._parse_result(
            "loading custom collections",
            lambda: [
                cookidoo_collection_from_json(cast(CustomCollectionJSON, item))
                for item in cast(Sequence[object], result["customlists"])
            ],
        )

    async def add(
        self,
        custom_collection_name: str,
    ) -> CookidooCollection:
        """Add custom collections.

        Parameters
        ----------
        custom_collection_name
            The custom collection name to add

        Returns
        -------
        CookidooCollection
            The added custom collection

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"title": custom_collection_name}
        url = self._client.api_endpoint / ADD_CUSTOM_COLLECTION_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post",
                url,
                "add custom collection",
                json=json_data,
                headers={"ACCEPT": CUSTOM_COLLECTIONS_PATH_ACCEPT},
            ),
            "add custom collection",
        )
        return self._client._parse_result(
            "loading added custom collection",
            lambda: cookidoo_collection_from_json(
                cast(CustomCollectionJSON, result["content"])
            ),
        )

    async def remove(
        self,
        custom_collection_id: str,
    ) -> None:
        """Remove custom collection.

        Parameters
        ----------
        custom_collection_id
            The custom collection id to remove

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / REMOVE_CUSTOM_COLLECTION_PATH.format(
            **self._client._cfg.localization.__dict__, id=custom_collection_id
        )
        await self._client._request_json(
            "delete",
            url,
            "remove custom collection",
            headers={"ACCEPT": CUSTOM_COLLECTIONS_PATH_ACCEPT},
            parse_response=False,
        )

    async def add_recipes(
        self,
        custom_collection_id: str,
        recipe_ids: builtins.list[str],
    ) -> CookidooCollection:
        """Add recipes to a custom collections.

        Parameters
        ----------
        custom_collection_id
            The custom collection to add the recipes to
        recipe_ids
            The recipe ids to add to a custom collection

        Returns
        -------
        CookidooCollection
            The changed custom collection

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"recipeIds": recipe_ids}
        url = self._client.api_endpoint / ADD_RECIPES_TO_CUSTOM_COLLECTION_PATH.format(
            **self._client._cfg.localization.__dict__, id=custom_collection_id
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "put", url, "add recipes to custom collection", json=json_data
            ),
            "add recipes to custom collection",
        )
        return self._client._parse_result(
            "loading added recipes",
            lambda: cookidoo_collection_from_json(
                cast(CustomCollectionJSON, result["content"])
            ),
        )

    async def remove_recipe(
        self,
        custom_collection_id: str,
        recipe_id: str,
    ) -> CookidooCollection:
        """Remove recipe from a custom collections.

        Parameters
        ----------
        custom_collection_id
            The custom collection to remove the recipe from
        recipe_id
            The recipe id to remove from a custom collection

        Returns
        -------
        CookidooCollection
            The changed custom collection

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / REMOVE_RECIPE_FROM_CUSTOM_COLLECTION_PATH.format(
            **self._client._cfg.localization.__dict__,
            id=custom_collection_id,
            recipe=recipe_id,
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "delete", url, "remove recipe from custom collection"
            ),
            "remove recipe from custom collection",
        )
        return self._client._parse_result(
            "loading removed recipe",
            lambda: cookidoo_collection_from_json(
                cast(CustomCollectionJSON, result["content"])
            ),
        )



class CookidooCollectionsService:
    """Cookidoo collection service namespace."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize collection sub-services."""
        self.managed = CookidooManagedCollectionsService(client)
        self.custom = CookidooCustomCollectionsService(client)
