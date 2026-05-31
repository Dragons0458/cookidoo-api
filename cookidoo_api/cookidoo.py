"""Cookidoo API v2 client facade."""

from urllib.parse import urlparse

from aiohttp import ClientSession
from yarl import URL

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.account import CookidooAccountService
from cookidoo_api.auth import CookidooAuthService
from cookidoo_api.calendar import CookidooCalendarService
from cookidoo_api.collections import CookidooCollectionsService
from cookidoo_api.const import DEFAULT_API_HEADERS
from cookidoo_api.custom_recipes import CookidooCustomRecipesService
from cookidoo_api.recipes import CookidooRecipesService
from cookidoo_api.shopping_list import CookidooShoppingListService
from cookidoo_api.types import CookidooConfig, CookidooLocalizationConfig


class Cookidoo(CookidooClientBase):
    """Unofficial Cookidoo API v2 interface."""

    auth: CookidooAuthService
    account: CookidooAccountService
    recipes: CookidooRecipesService
    custom_recipes: CookidooCustomRecipesService
    shopping_list: CookidooShoppingListService
    collections: CookidooCollectionsService
    calendar: CookidooCalendarService

    def __init__(
        self,
        session: ClientSession,
        cfg: CookidooConfig = CookidooConfig(),
    ) -> None:
        """Init function for Cookidoo API."""
        self._session = session
        self._cfg = cfg
        self._api_headers = DEFAULT_API_HEADERS.copy()
        self._logged_in = False
        self.auth = CookidooAuthService(self)
        self.account = CookidooAccountService(self)
        self.recipes = CookidooRecipesService(self)
        self.custom_recipes = CookidooCustomRecipesService(self)
        self.shopping_list = CookidooShoppingListService(self)
        self.collections = CookidooCollectionsService(self)
        self.calendar = CookidooCalendarService(self)

    @property
    def localization(self) -> CookidooLocalizationConfig:
        """Localization."""
        return self._cfg.localization

    @property
    def api_endpoint(self) -> URL:
        """Get the API endpoint derived from the configured localization."""
        parsed = urlparse(self._cfg.localization.url)
        return URL(f"{parsed.scheme}://{parsed.netloc}")
