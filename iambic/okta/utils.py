from __future__ import annotations

import asyncio
import json

import okta.models as models
from okta.errors.okta_api_error import OktaAPIError

from iambic.core.exceptions import RateLimitException


async def generate_user_profile(user: models.User):
    """
    Generates a key-value pair of user profile attributes that aren't None.
    This is useful to keep user templates small.
    """
    return {k: v for (k, v) in user.profile.__dict__.items() if v is not None}


async def handle_okta_fn(fn, *args, **kwargs):
    try:
        res = await fn(*args, **kwargs)
    except asyncio.exceptions.TimeoutError:
        raise asyncio.exceptions.TimeoutError

    err = res[-1]
    if err:
        if isinstance(err, Exception):
            raise err
        # Handle the case where Okta SDK returns appropriately scoped OktaAPIError
        if isinstance(err, OktaAPIError):
            if err.error_code == "E0000047":
                raise RateLimitException(err.error_summary)
            return res
        # Handle the case where Okta SDK returns JSON
        try:
            err_j = json.loads(err)
            if err_j.get("errorCode") == "E0000047":
                raise RateLimitException(err)
        except TypeError:
            pass
        print("here")
    return res
