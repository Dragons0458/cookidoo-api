"""Cookidoo custom recipe service."""

from typing import cast

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import (
    ADD_CUSTOM_RECIPE_PATH,
    CUSTOM_RECIPE_PATH,
    RECIPE_PATH,
    REMOVE_CUSTOM_RECIPE_PATH,
)
from cookidoo_api.helpers import cookidoo_custom_recipe_from_json
from cookidoo_api.raw_types import CustomRecipeJSON
from cookidoo_api.types import CookidooCustomRecipe


class CookidooCustomRecipesService:
    """CookidooCustomRecipes service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo custom recipe service."""
        self._client = client

    async def get(self, id: str) -> CookidooCustomRecipe:
        """Get custom recipe.

        Parameters
        ----------
        id
            The id of the custom recipe

        Returns
        -------
        CookidooCustomRecipe
            The custom recipe

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / CUSTOM_RECIPE_PATH.format(
            **self._client._cfg.localization.__dict__, id=id
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading custom recipe"),
            "loading custom recipe",
        )
        return self._client._parse_result(
            "loading custom recipe",
            lambda: cookidoo_custom_recipe_from_json(
                cast(CustomRecipeJSON, result),
                self._client._cfg.localization,
            ),
        )

    async def add_from(
        self, recipe_id: str, serving_size: int
    ) -> CookidooCustomRecipe:
        """Add custom recipe.

        Parameters
        ----------
        recipe_id
            The base recipe to copy
        serving_size
            The serving size of the custom recipe

        Returns
        -------
        CookidooCustomRecipe
            The added custom recipe

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
            "recipeUrl": str(
                self._client.api_endpoint
                / RECIPE_PATH.format(**self._client._cfg.localization.__dict__, id=recipe_id)
            ),
            "serving_size": serving_size,
        }
        url = self._client.api_endpoint / ADD_CUSTOM_RECIPE_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("post", url, "add custom recipe", json=json_data),
            "add custom recipe",
        )
        return self._client._parse_result(
            "add custom recipe",
            lambda: cookidoo_custom_recipe_from_json(
                cast(CustomRecipeJSON, result),
                self._client._cfg.localization,
            ),
        )

    async def remove(
        self,
        custom_recipe_id: str,
    ) -> None:
        """Remove custom recipe.

        Parameters
        ----------
        custom_recipe_id
            The custom recipe id to remove

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / REMOVE_CUSTOM_RECIPE_PATH.format(
            **self._client._cfg.localization.__dict__, id=custom_recipe_id
        )
        await self._client._request_json(
            "delete", url, "remove custom recipe", parse_response=False
        )
