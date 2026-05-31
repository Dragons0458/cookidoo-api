#!/usr/bin/env python3
"""Example script for cookidoo-api."""

import asyncio
from datetime import datetime
import logging
import os
import sys

import aiohttp
from dotenv import load_dotenv

from cookidoo_api import Cookidoo
from cookidoo_api.helpers import (
    get_country_options,
    get_language_options,
    get_localization_options,
)
from cookidoo_api.types import (
    CookidooAdditionalItem,
    CookidooConfig,
    CookidooIngredientItem,
)

load_dotenv()

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, etc.)
    format="%(asctime)s [%(levelname)8s] %(name)s:%(lineno)s %(message)s",  # Format of the log messages
    handlers=[  # Specify the handlers for the logger
        logging.StreamHandler(sys.stdout)  # Output to stdout
    ],
)


async def main():
    """Run main example function."""
    # Use CookieJar(unsafe=True) to support cross-domain cookies during login
    jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        # Show all country_codes, languages and some localizations
        _country_codes = await get_country_options()
        _languages = await get_language_options()
        _localizations_ch = await get_localization_options(country="ch")
        _localizations_en = await get_localization_options(language="en")

        # Create Cookidoo instance with email and password
        cookidoo = Cookidoo(
            session,
            cfg=CookidooConfig(
                email=os.environ["EMAIL"],
                password=os.environ["PASSWORD"],
                localization=(
                    await get_localization_options(country="ie", language="en-GB")
                )[0],
            ),
        )

        # Try to load saved cookies, otherwise login fresh
        cookie_file = ".cookies"
        try:
            cookidoo.auth.load_cookies(cookie_file)
        except Exception:
            await cookidoo.auth.login()
            cookidoo.auth.save_cookies(cookie_file)

        # Info
        await cookidoo.account.get_user_info()
        subscription = await cookidoo.account.get_active_subscription()

        # Some features are only available for premium accounts. To get a premium account, you need to subscribe to the Cookidoo service. When creating a new account, you get 1 month of premium for free which is enough to test the premium features :)
        ENABLE_PREMIUM = subscription and subscription.active

        # Custom collections
        added_custom_collection = await cookidoo.collections.custom.add(
            "TEST_COLLECTION"
        )
        _custom_collections = await cookidoo.collections.custom.list()
        await cookidoo.collections.custom.add_recipes(
            added_custom_collection.id, ["r907015"]
        )
        _custom_collections = await cookidoo.collections.custom.list()
        await cookidoo.collections.custom.remove_recipe(
            added_custom_collection.id, "r907015"
        )
        _custom_collections = await cookidoo.collections.custom.list()
        await cookidoo.collections.custom.remove(added_custom_collection.id)

        # # Managed collections
        _added_managed_collection = await cookidoo.collections.managed.add("col500401")
        _managed_collections = await cookidoo.collections.managed.list()
        await cookidoo.collections.managed.remove("col500401")

        # Recipe details
        _recipe_details = await cookidoo.recipes.get_details("r59322")

        if ENABLE_PREMIUM:
            # Custom recipe
            added_custom_recipe = await cookidoo.custom_recipes.add_from(
                "r59322", _recipe_details.serving_size
            )
            _custom_recipe = await cookidoo.custom_recipes.get(added_custom_recipe.id)

        # Calendar recipes
        _added_recipes_to_calendar = await cookidoo.calendar.add_recipes(
            datetime.now().date(), ["r907015", "r59322"]
        )
        if ENABLE_PREMIUM:
            _added_custom_recipes_to_calendar = (
                await cookidoo.calendar.add_custom_recipes(
                    datetime.now().date(), [added_custom_recipe.id]
                )
            )
        _recipes_in_calendar = await cookidoo.calendar.week(
            datetime.now().date()
        )
        _removed_recipes_from_calendar = await cookidoo.calendar.remove_recipe(
            datetime.now().date(), "r907015"
        )
        _removed_recipes_from_calendar = await cookidoo.calendar.remove_recipe(
            datetime.now().date(), "r59322"
        )
        if ENABLE_PREMIUM:
            _removed_custom_recipes_from_calendar = (
                await cookidoo.calendar.remove_custom_recipe(
                    datetime.now().date(), added_custom_recipe.id
                )
            )
        _recipes_in_calendar = await cookidoo.calendar.week(
            datetime.now().date()
        )

        # Shopping list
        await cookidoo.shopping_list.clear()

        # Ingredients
        added_ingredients = await cookidoo.shopping_list.add_ingredient_items_for_recipes(
            ["r59322", "r907016"]
        )
        _edited_ingredients = await cookidoo.shopping_list.edit_ingredient_items_ownership(
            [
                CookidooIngredientItem(
                    **{**ingredient.__dict__, "is_owned": not ingredient.is_owned},
                )
                for ingredient in filter(
                    lambda ingredient: ingredient.name == "Hefe",
                    added_ingredients,
                )
            ]
        )
        _ingredients = await cookidoo.shopping_list.ingredients()
        _recipes = await cookidoo.shopping_list.recipes()
        await cookidoo.shopping_list.remove_ingredient_items_for_recipes(["r59322"])

        if ENABLE_PREMIUM:
            added_ingredients = await cookidoo.shopping_list.add_ingredient_items_for_custom_recipes(
                [added_custom_recipe.id]
            )
            _edited_ingredients = await cookidoo.shopping_list.edit_ingredient_items_ownership(
                [
                    CookidooIngredientItem(
                        **{**ingredient.__dict__, "is_owned": not ingredient.is_owned},
                    )
                    for ingredient in filter(
                        lambda ingredient: "Hefe" in ingredient.name,
                        added_ingredients,
                    )
                ]
            )

            _ingredients = await cookidoo.shopping_list.ingredients()
            _recipes = await cookidoo.shopping_list.recipes()
            await cookidoo.shopping_list.remove_ingredient_items_for_custom_recipes(
                [added_custom_recipe.id]
            )

            # Remove after usage
            await cookidoo.custom_recipes.remove(added_custom_recipe.id)

        # Additional items
        added_additional_items = await cookidoo.shopping_list.add_additional_items(
            ["Fleisch", "Fisch"]
        )
        edited_additional_items = await cookidoo.shopping_list.edit_additional_items_ownership(
            [
                CookidooAdditionalItem(
                    **{
                        **additional_item.__dict__,
                        "is_owned": not additional_item.is_owned,
                    },
                )
                for additional_item in filter(
                    lambda additional_item: additional_item.name == "Fisch",
                    added_additional_items,
                )
            ]
        )
        await cookidoo.shopping_list.edit_additional_items(
            [
                CookidooAdditionalItem(
                    **{
                        **additional_item.__dict__,
                        "is_owned": "Vogel",
                    },
                )
                for additional_item in filter(
                    lambda additional_item: additional_item.name == "Fisch",
                    edited_additional_items,
                )
            ]
        )
        _additional_items = await cookidoo.shopping_list.additional_items()
        await cookidoo.shopping_list.remove_additional_items(
            [
                added_additional_item.id
                for added_additional_item in added_additional_items
            ]
        )


asyncio.run(main())
