"""Cookidoo shopping list service."""

from collections.abc import Mapping, Sequence
import time
from typing import cast

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import (
    ADD_ADDITIONAL_ITEMS_PATH,
    ADD_INGREDIENT_ITEMS_FOR_RECIPES_PATH,
    ADDITIONAL_ITEMS_PATH,
    EDIT_ADDITIONAL_ITEMS_PATH,
    EDIT_OWNERSHIP_ADDITIONAL_ITEMS_PATH,
    EDIT_OWNERSHIP_INGREDIENT_ITEMS_PATH,
    INGREDIENT_ITEMS_PATH,
    REMOVE_ADDITIONAL_ITEMS_PATH,
    REMOVE_INGREDIENT_ITEMS_FOR_RECIPES_PATH,
    SHOPPING_LIST_RECIPES_PATH,
)
from cookidoo_api.helpers import (
    cookidoo_additional_item_from_json,
    cookidoo_ingredient_item_from_json,
    cookidoo_recipe_from_json,
)
from cookidoo_api.raw_types import AdditionalItemJSON, ItemJSON, RecipeJSON
from cookidoo_api.types import (
    CookidooAdditionalItem,
    CookidooIngredientItem,
    CookidooShoppingRecipe,
)


class CookidooShoppingListService:
    """CookidooShoppingList service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo shopping list service."""
        self._client = client

    async def recipes(
        self,
    ) -> list[CookidooShoppingRecipe]:
        """Get recipes.

        Returns
        -------
        list[CookidooShoppingRecipe]
            The list of the recipes

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / SHOPPING_LIST_RECIPES_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading recipes"),
            "loading recipes",
        )
        return self._client._parse_result(
            "loading recipes",
            lambda: [
                cookidoo_recipe_from_json(
                    cast(RecipeJSON, recipe), self._client._cfg.localization
                )
                for recipe in [
                    *cast(Sequence[object], result["recipes"]),
                    *cast(Sequence[object], result["customerRecipes"]),
                ]
            ],
        )

    async def ingredients(
        self,
    ) -> list[CookidooIngredientItem]:
        """Get ingredient items.

        Returns
        -------
        list[CookidooIngredientItem]
            The list of the ingredient items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / INGREDIENT_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading ingredient items"),
            "loading ingredient items",
        )
        return self._client._parse_result(
            "loading ingredient items",
            lambda: [
                cookidoo_ingredient_item_from_json(cast(ItemJSON, ingredient))
                for recipe in [
                    *cast(Sequence[Mapping[str, object]], result["recipes"]),
                    *cast(Sequence[Mapping[str, object]], result["customerRecipes"]),
                ]
                for ingredient in cast(
                    Sequence[object], recipe["recipeIngredientGroups"]
                )
            ],
        )

    async def add_ingredient_items_for_recipes(
        self,
        recipe_ids: list[str],
    ) -> list[CookidooIngredientItem]:
        """Add ingredient items for recipes.

        Parameters
        ----------
        recipe_ids
            The recipe ids for the ingredient items to add to the shopping list

        Returns
        -------
        list[CookidooIngredientItem]
            The list of the added ingredient items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"recipeIDs": recipe_ids}
        url = self._client.api_endpoint / ADD_INGREDIENT_ITEMS_FOR_RECIPES_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post", url, "add ingredient items for recipes", json=json_data
            ),
            "add ingredient items for recipes",
        )
        return self._client._parse_result(
            "loading added ingredient items",
            lambda: [
                cookidoo_ingredient_item_from_json(cast(ItemJSON, ingredient))
                for recipe in cast(Sequence[Mapping[str, object]], result["data"])
                for ingredient in cast(
                    Sequence[object], recipe["recipeIngredientGroups"]
                )
            ],
        )

    async def remove_ingredient_items_for_recipes(
        self,
        recipe_ids: list[str],
    ) -> None:
        """Remove ingredient items for recipes.

        Parameters
        ----------
        recipe_ids
            The recipe ids for the ingredient items to remove to the shopping list

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"recipeIDs": recipe_ids}
        url = self._client.api_endpoint / REMOVE_INGREDIENT_ITEMS_FOR_RECIPES_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        await self._client._request_json(
            "post",
            url,
            "remove ingredient items for recipes",
            json=json_data,
            parse_response=False,
        )

    async def edit_ingredient_items_ownership(
        self,
        ingredient_items: list[CookidooIngredientItem],
    ) -> list[CookidooIngredientItem]:
        """Edit ownership ingredient items.

        Parameters
        ----------
        ingredient_items
            The ingredient items to change the the `is_owned` value for

        Returns
        -------
        list[CookidooIngredientItem]
            The list of the edited ingredient items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {
            "ingredients": [
                {
                    "id": ingredient_item.id,
                    "isOwned": ingredient_item.is_owned,
                    "ownedTimestamp": int(time.time()),
                }
                for ingredient_item in ingredient_items
            ]
        }
        url = self._client.api_endpoint / EDIT_OWNERSHIP_INGREDIENT_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post", url, "edit ingredient items ownership", json=json_data
            ),
            "edit ingredient items ownership",
        )
        return self._client._parse_result(
            "loading edited ingredient items",
            lambda: [
                cookidoo_ingredient_item_from_json(cast(ItemJSON, ingredient))
                for ingredient in cast(Sequence[object], result["data"])
            ],
        )

    async def add_ingredient_items_for_custom_recipes(
        self,
        recipe_ids: list[str],
    ) -> list[CookidooIngredientItem]:
        """Add ingredient items for custom recipes.

        Parameters
        ----------
        recipe_ids
            The recipe ids for the ingredient items to add to the shopping list

        Returns
        -------
        list[CookidooIngredientItem]
            The list of the added ingredient items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {
            "recipeIDs": [
                {"id": recipe_id, "source": "CUSTOMER"} for recipe_id in recipe_ids
            ]
        }
        url = self._client.api_endpoint / ADD_INGREDIENT_ITEMS_FOR_RECIPES_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post", url, "add ingredient items for custom recipes", json=json_data
            ),
            "add ingredient items for custom recipes",
        )
        return self._client._parse_result(
            "loading added ingredient items",
            lambda: [
                cookidoo_ingredient_item_from_json(cast(ItemJSON, ingredient))
                for recipe in cast(Sequence[Mapping[str, object]], result["data"])
                for ingredient in cast(
                    Sequence[object], recipe["recipeIngredientGroups"]
                )
            ],
        )

    async def remove_ingredient_items_for_custom_recipes(
        self,
        recipe_ids: list[str],
    ) -> None:
        """Remove ingredient items for custom recipes.

        Parameters
        ----------
        recipe_ids
            The custom recipe ids for the ingredient items to remove to the shopping list

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"recipeIDs": recipe_ids}
        url = self._client.api_endpoint / REMOVE_INGREDIENT_ITEMS_FOR_RECIPES_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        await self._client._request_json(
            "post",
            url,
            "remove ingredient items for custom recipes",
            json=json_data,
            parse_response=False,
        )

    async def additional_items(
        self,
    ) -> list[CookidooAdditionalItem]:
        """Get additional items.

        Returns
        -------
        list[CookidooAdditionalItem]
            The list of the additional items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / ADDITIONAL_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading additional items"),
            "loading additional items",
        )
        return self._client._parse_result(
            "loading additional items",
            lambda: [
                cookidoo_additional_item_from_json(
                    cast(AdditionalItemJSON, additional_item)
                )
                for additional_item in cast(Sequence[object], result["additionalItems"])
            ],
        )

    async def add_additional_items(
        self,
        additional_item_names: list[str],
    ) -> list[CookidooAdditionalItem]:
        """Create additional items.

        Parameters
        ----------
        additional_item_names
            The additional item names to create, only the label can be set, as the default state `is_owned=false` is forced (chain with immediate update call for work-around)

        Returns
        -------
        list[CookidooAdditionalItem]
            The list of the added additional items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"itemsValue": additional_item_names}
        url = self._client.api_endpoint / ADD_ADDITIONAL_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post", url, "add additional items", json=json_data
            ),
            "add additional items",
        )
        return self._client._parse_result(
            "loading added additional items",
            lambda: [
                cookidoo_additional_item_from_json(
                    cast(AdditionalItemJSON, additional_item)
                )
                for additional_item in cast(Sequence[object], result["data"])
            ],
        )

    async def edit_additional_items(
        self,
        additional_items: list[CookidooAdditionalItem],
    ) -> list[CookidooAdditionalItem]:
        """Edit additional items.

        Parameters
        ----------
        additional_items
            The additional items to change the the `name` value for

        Returns
        -------
        list[CookidooAdditionalItem]
            The list of the edited additional items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {
            "additionalItems": [
                {
                    "id": additional_item.id,
                    "name": additional_item.name,
                }
                for additional_item in additional_items
            ]
        }
        url = self._client.api_endpoint / EDIT_ADDITIONAL_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post", url, "edit additional items", json=json_data
            ),
            "edit additional items",
        )
        return self._client._parse_result(
            "loading edited additional items",
            lambda: [
                cookidoo_additional_item_from_json(
                    cast(AdditionalItemJSON, additional_item)
                )
                for additional_item in cast(Sequence[object], result["data"])
            ],
        )

    async def edit_additional_items_ownership(
        self,
        additional_items: list[CookidooAdditionalItem],
    ) -> list[CookidooAdditionalItem]:
        """Edit ownership additional items.

        Parameters
        ----------
        additional_items
            The additional items to change the the `is_owned` value for

        Returns
        -------
        list[CookidooAdditionalItem]
            The list of the edited additional items

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {
            "additionalItems": [
                {
                    "id": additional_item.id,
                    "isOwned": additional_item.is_owned,
                    "ownedTimestamp": int(time.time()),
                }
                for additional_item in additional_items
            ]
        }
        url = self._client.api_endpoint / EDIT_OWNERSHIP_ADDITIONAL_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "post", url, "edit additional items ownership", json=json_data
            ),
            "edit additional items ownership",
        )
        return self._client._parse_result(
            "loading edited additional items",
            lambda: [
                cookidoo_additional_item_from_json(
                    cast(AdditionalItemJSON, additional_item)
                )
                for additional_item in cast(Sequence[object], result["data"])
            ],
        )

    async def remove_additional_items(
        self,
        additional_item_ids: list[str],
    ) -> None:
        """Remove additional items.

        Parameters
        ----------
        additional_item_ids
            The additional item ids to remove

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"additionalItemIDs": additional_item_ids}
        url = self._client.api_endpoint / REMOVE_ADDITIONAL_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        await self._client._request_json(
            "post",
            url,
            "remove additional items",
            json=json_data,
            parse_response=False,
        )

    async def clear(
        self,
    ) -> None:
        """Remove all additional items, ingredients and recipes.

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / INGREDIENT_ITEMS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        await self._client._request_json(
            "delete", url, "clear shopping list", parse_response=False
        )
