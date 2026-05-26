import logging
import os

import httpx

logger = logging.getLogger("backend")

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


async def verify(token: str, remote_ip: str | None = None) -> bool:
    secret = os.environ.get("TURNSTILE_SECRET")
    if not secret:
        logger.warning("TURNSTILE_SECRET not set; allowing request (dev mode)")
        return True
    data = {"secret": secret, "response": token}
    if remote_ip:
        data["remoteip"] = remote_ip
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(VERIFY_URL, data=data)
            result = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.warning("Turnstile verify failed: %s", e)
        return False
    return bool(result.get("success"))
