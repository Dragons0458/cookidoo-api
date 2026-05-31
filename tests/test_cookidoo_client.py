"""Unit tests for cookidoo-api."""


from aiohttp import ClientSession
from aioresponses import aioresponses
from dotenv import load_dotenv
import pytest

import cookidoo_api
from cookidoo_api.cookidoo import Cookidoo
from cookidoo_api.helpers import get_localization_options
from cookidoo_api.types import CookidooConfig

load_dotenv()


def test_api_version() -> None:
    """Test package and public API versions."""
    assert cookidoo_api.__version__ == "2.0.0"
    assert cookidoo_api.__api_version__ == "2"

class TestGetterSetter:
    """Tests for getter and setter."""

    @pytest.mark.parametrize(
        ("country", "language", "expected_domain"),
        [
            ("ch", "de-CH", "https://cookidoo.ch"),
            ("de", "de-DE", "https://cookidoo.de"),
            ("ma", "en", "https://cookidoo.international"),
            ("ie", "en-GB", "https://cookidoo.co.uk"),
            ("gb", "en-GB", "https://cookidoo.co.uk"),
        ],
    )
    async def test_api_endpoint(
        self,
        mocked: aioresponses,
        session: ClientSession,
        country: str,
        language: str,
        expected_domain: str,
    ) -> None:
        """Test api endpoint for different localizations."""
        cookidoo = Cookidoo(
            session,
            cfg=CookidooConfig(
                localization=(
                    await get_localization_options(country=country, language=language)
                )[0],
            ),
        )

        assert str(cookidoo.api_endpoint) == expected_domain

    async def test_localization(self, cookidoo: Cookidoo) -> None:
        """Test localization property."""
        loc = cookidoo.localization
        assert loc.language == "de-CH"
        assert loc.country_code == "ch"
