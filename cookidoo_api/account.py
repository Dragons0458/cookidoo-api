"""Cookidoo account service."""

from collections.abc import Mapping
from typing import cast

from cookidoo_api._client import CookidooClientBase
from cookidoo_api.const import COMMUNITY_PROFILE_PATH, SUBSCRIPTIONS_PATH
from cookidoo_api.exceptions import CookidooParseException
from cookidoo_api.helpers import (
    cookidoo_subscription_from_json,
    cookidoo_user_info_from_json,
)
from cookidoo_api.raw_types import CommunityProfileJSON, SubscriptionJSON
from cookidoo_api.types import CookidooSubscription, CookidooUserInfo


class CookidooAccountService:
    """CookidooAccount service."""

    def __init__(self, client: CookidooClientBase) -> None:
        """Initialize Cookidoo account service."""
        self._client = client

    async def get_user_info(
        self,
    ) -> CookidooUserInfo:
        """Get user info.

        Returns
        -------
        CookidooUserInfo
            The user info

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / COMMUNITY_PROFILE_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        result = self._client._ensure_mapping(
            await self._client._request_json("get", url, "loading user info"),
            "loading user info",
        )
        return self._client._parse_result(
            "loading user info",
            lambda: cookidoo_user_info_from_json(cast(CommunityProfileJSON, result)),
        )

    async def get_active_subscription(
        self,
    ) -> CookidooSubscription | None:
        """Get active subscription if any.

        Returns
        -------
        CookidooSubscription
            The active subscription

        Raises
        ------
        CookidooAuthException
            When the access token is not valid anymore
        CookidooRequestException
            If the request fails.
        CookidooParseException
            If the parsing of the request response fails.

        """

        url = self._client.api_endpoint / SUBSCRIPTIONS_PATH.format(
            **self._client._cfg.localization.__dict__
        )
        subscriptions = self._client._ensure_sequence(
            await self._client._request_json("get", url, "loading active subscription"),
            "loading active subscription",
        )
        try:
            if subscription := next(
                (
                    subscription
                    for subscription in subscriptions
                    if isinstance(subscription, Mapping) and subscription["active"]
                ),
                None,
            ):
                return self._client._parse_result(
                    "loading active subscription",
                    lambda: cookidoo_subscription_from_json(
                        cast(SubscriptionJSON, subscription)
                    ),
                )
        except KeyError as e:
            raise CookidooParseException(
                "Loading active subscription failed during parsing of request response."
            ) from e
        return None
