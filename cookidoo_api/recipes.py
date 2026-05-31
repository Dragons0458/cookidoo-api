"""Cookidoo recipe service."""

from typing import cast

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import RECIPE_PATH
from cookidoo_api.exceptions import CookidooParseException
from cookidoo_api.helpers import (
    cookidoo_recipe_details_from_json,
    cookidoo_search_result_from_json,
    normalize_list_param,
    normalize_tmv_param,
)
from cookidoo_api.raw_types import RecipeDetailsJSON, SearchResultJSON
from cookidoo_api.types import (
    CookidooSearchResult,
    CookidooShoppingRecipeDetails,
    ThermomixMachineType,
)


class CookidooRecipesService:
    """CookidooRecipes service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo recipe service."""
        self._client = client

    async def get_details(self, id: str) -> CookidooShoppingRecipeDetails:
        """Get recipe details.

        Parameters
        ----------
        id
            The id of the recipe

        Returns
        -------
        CookidooShoppingRecipeDetails
            The recipe details

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / RECIPE_PATH.format(
            **self._client._cfg.localization.__dict__, id=id
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading recipe details"),
            "loading recipe details",
        )
        return self._client._parse_result(
            "loading recipe details",
            lambda: cookidoo_recipe_details_from_json(
                cast(RecipeDetailsJSON, result),
                self._client._cfg.localization,
            ),
        )

    async def search(
        self,
        query: str | None = None,
        locale: str | None = None,
        accessories: str | list[str] | None = None,
        languages: str | list[str] | None = None,
        categories: str | list[str] | None = None,
        countries: str | list[str] | None = None,
        ingredients: str | list[str] | None = None,
        exclude_ingredients: str | list[str] | None = None,
        tags: str | list[str] | None = None,
        ratings: str | list[str] | None = None,
        difficulty: str | None = None,
        preparation_time: int | None = None,
        total_time: int | None = None,
        portions: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        tmv: ThermomixMachineType
        | str
        | list[ThermomixMachineType | str]
        | None = None,
    ) -> CookidooSearchResult:
        """Search recipes in Cookidoo (GET).

        Uses the same API base as the rest of the client (api_endpoint):
        {api_endpoint}/search/{locale}

        Parameters
        ----------
        query
            Optional search query (e.g. "chicken", "pasta").
        locale
            Locale for the search path (e.g. "es", "en", "de").
            Defaults to the first part of the configured language (e.g. "de-CH" -> "de").
        accessories
            Optional comma-separated accessory filters
            (e.g. "includingFriend,includingBladeCover,includingBladeCoverWithPeeler,includingCutter,includingSensor").
        languages
            Optional comma-separated language codes (e.g. "en,es").
        categories
            Optional comma-separated category IDs.
        countries
            Optional comma-separated country codes (e.g. "ar").
        ingredients
            Optional comma-separated ingredients.
        exclude_ingredients
            Optional comma-separated excluded ingredients.
        tags
            Optional comma-separated tags.
        ratings
            Optional comma-separated ratings (e.g. "5,4").
        difficulty
            Optional difficulty (e.g. "easy", "medium", "hard").
        preparation_time
            Optional preparation time in seconds.
        total_time
            Optional total time in seconds.
        portions
            Optional portions count.
        page
            Optional page number (API-dependent, often 0- or 1-based).
        page_size
            Optional page size (API-dependent; common keys: pageSize).
        tmv
            Optional Thermomix machine version. Use ``ThermomixMachineType``
            (e.g. ``ThermomixMachineType.TM7``) or a string ("TM7", "TM6", "TM5").

        Returns
        -------
        CookidooSearchResult
            Search result with recipes and total count.

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore.
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        if locale is None:
            locale = self._client._cfg.localization.language.split("-")[0]
        url = self._client.api_endpoint / "search" / locale
        params: dict[str, str] = {}
        if query is not None:
            params["query"] = query
        if accessories is not None and (
            normalized := normalize_list_param(accessories)
        ):
            params["accessories"] = normalized
        if languages is not None and (normalized := normalize_list_param(languages)):
            params["languages"] = normalized
        if categories is not None and (normalized := normalize_list_param(categories)):
            params["categories"] = normalized
        if countries is not None and (normalized := normalize_list_param(countries)):
            params["countries"] = normalized
        if ingredients is not None and (
            normalized := normalize_list_param(ingredients)
        ):
            params["ingredients"] = normalized
        if exclude_ingredients is not None and (
            normalized := normalize_list_param(exclude_ingredients)
        ):
            params["excludeIngredients"] = normalized
        if tags is not None and (normalized := normalize_list_param(tags)):
            params["tags"] = normalized
        if ratings is not None and (normalized := normalize_list_param(ratings)):
            params["ratings"] = normalized
        if difficulty is not None:
            params["difficulty"] = difficulty
        if preparation_time is not None:
            params["preparationTime"] = str(preparation_time)
        if total_time is not None:
            params["totalTime"] = str(total_time)
        if portions is not None:
            params["portions"] = str(portions)
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["pageSize"] = str(page_size)
        if tmv is not None and (normalized := normalize_tmv_param(tmv)):
            params["tmv"] = normalized
        result = await self._client._request_json("get", url, "search recipes", params=params)
        if result is None:
            return CookidooSearchResult(recipes=[], total=0)
        if not isinstance(result, dict):
            raise CookidooParseException(
                "Search recipes failed during parsing of request response."
            )
        return cookidoo_search_result_from_json(
            cast(SearchResultJSON, result), self._client._cfg.localization
        )
