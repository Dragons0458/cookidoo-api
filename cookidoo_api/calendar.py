"""Cookidoo calendar service."""

from collections.abc import Sequence
from datetime import date
from typing import cast

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import (
    ADD_RECIPES_TO_CALENDER_PATH,
    RECIPES_IN_CALENDAR_WEEK_PATH,
    REMOVE_RECIPE_FROM_CALENDER_PATH,
)
from cookidoo_api.helpers import cookidoo_calendar_day_from_json
from cookidoo_api.raw_types import CalendarDayJSON
from cookidoo_api.types import CookidooCalendarDay


class CookidooCalendarService:
    """CookidooCalendar service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo calendar service."""
        self._client = client

    async def week(
        self, day: date
    ) -> list[CookidooCalendarDay]:
        """Get recipes in a calendar week.

        Parameters
        ----------
        day
            The date specifying the calendar week

        Returns
        -------
        list[CookidooCalendarDay]
            The list of the calendar days with recipes

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / RECIPES_IN_CALENDAR_WEEK_PATH.format(
            **self._client._cfg.localization.__dict__, day=day.isoformat()
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading recipes in calendar week"),
            "loading recipes in calendar week",
        )
        return self._client._parse_result(
            "loading recipes in calendar week",
            lambda: [
                cookidoo_calendar_day_from_json(
                    cast(CalendarDayJSON, calendar_day), self._client._cfg.localization
                )
                for calendar_day in cast(Sequence[object], result["myDays"])
            ],
        )

    async def add_recipes(
        self,
        day: date,
        recipe_ids: list[str],
    ) -> CookidooCalendarDay:
        """Add recipes to a calendar.

        Parameters
        ----------
        day
            The date to add the recipes to in the calendar
        recipe_ids
            The recipe ids to add to the calendar

        Returns
        -------
        CookidooCalendarDay
            The changed calendar day

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        json_data = {"recipeIds": recipe_ids, "dayKey": day.isoformat()}
        url = self._client.api_endpoint / ADD_RECIPES_TO_CALENDER_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "put", url, "add recipes to calendar", json=json_data
            ),
            "add recipes to calendar",
        )
        return self._client._parse_result(
            "loading added recipes",
            lambda: cookidoo_calendar_day_from_json(
                cast(CalendarDayJSON, result["content"]),
                self._client._cfg.localization,
            ),
        )

    async def remove_recipe(
        self,
        day: date,
        recipe_id: str,
    ) -> CookidooCalendarDay:
        """Remove recipe from calendar.

        Parameters
        ----------
        day
            The date to remove the recipe from in the calendar
        recipe_id
            The recipe id to remove from the calendar

        Returns
        -------
        CookidooCalendarDay
            The changed calendar day

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / REMOVE_RECIPE_FROM_CALENDER_PATH.format(
            **self._client._cfg.localization.__dict__,
            day=day.isoformat(),
            recipe=recipe_id,
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("delete", url, "remove recipe from calendar"),
            "remove recipe from calendar",
        )
        return self._client._parse_result(
            "loading removed recipe",
            lambda: cookidoo_calendar_day_from_json(
                cast(CalendarDayJSON, result["content"]),
                self._client._cfg.localization,
            ),
        )

    async def add_custom_recipes(
        self,
        day: date,
        recipe_ids: list[str],
    ) -> CookidooCalendarDay:
        """Add custom recipes to a calendar.

        Parameters
        ----------
        day
            The date to add the custom recipes to in the calendar
        recipe_ids
            The recipe ids to add to the calendar

        Returns
        -------
        CookidooCalendarDay
            The changed calendar day

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
            "recipeIds": recipe_ids,
            "dayKey": day.isoformat(),
            "recipeSource": "CUSTOMER",
        }
        url = self._client.api_endpoint / ADD_RECIPES_TO_CALENDER_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "put", url, "add custom recipes to calendar", json=json_data
            ),
            "add custom recipes to calendar",
        )
        return self._client._parse_result(
            "loading added custom recipes",
            lambda: cookidoo_calendar_day_from_json(
                cast(CalendarDayJSON, result["content"]),
                self._client._cfg.localization,
            ),
        )

    async def remove_custom_recipe(
        self,
        day: date,
        recipe_id: str,
    ) -> CookidooCalendarDay:
        """Remove custom recipe from calendar.

        Parameters
        ----------
        day
            The date to remove the custom recipe from in the calendar
        recipe_id
            The custom recipe id to remove from the calendar

        Returns
        -------
        CookidooCalendarDay
            The changed calendar day

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """
        url = self._client.api_endpoint / REMOVE_RECIPE_FROM_CALENDER_PATH.format(
            **self._client._cfg.localization.__dict__,
            day=day.isoformat(),
            recipe=recipe_id,
        )
        result = self._client._ensure_mapping(
            await self._client._request_json(
                "delete",
                url,
                "remove custom recipe from calendar",
                params={"recipeSource": "CUSTOMER"},
            ),
            "remove custom recipe from calendar",
        )
        return self._client._parse_result(
            "loading custom removed recipe",
            lambda: cookidoo_calendar_day_from_json(
                cast(CalendarDayJSON, result["content"]),
                self._client._cfg.localization,
            ),
        )
