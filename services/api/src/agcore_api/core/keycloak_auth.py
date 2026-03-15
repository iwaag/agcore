from typing import Any

import httpx

from core.common import (
    CLIEND_ID,
    KEYCLOAK_CLIENT_SECRET,
    KEYCLOAK_TOKEN_ENDPOINT,
)


class KeycloakAuthError(RuntimeError):
    pass


async def exchange_token_for_own_client(
    subject_token: str,
    timeout_seconds: float = 5.0,
) -> dict[str, Any]:
    if not CLIEND_ID:
        raise KeycloakAuthError("CLIENT_ID is not configured")

    form_data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "client_id": CLIEND_ID,
        "subject_token": subject_token,
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
    }
    if KEYCLOAK_CLIENT_SECRET:
        form_data["client_secret"] = KEYCLOAK_CLIENT_SECRET

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(KEYCLOAK_TOKEN_ENDPOINT, data=form_data)

    if response.status_code >= 400:
        raise KeycloakAuthError(
            f"Token exchange failed ({response.status_code}): {response.text}"
        )

    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise KeycloakAuthError("Keycloak response did not contain access_token")

    return payload


async def issue_own_client_access_token(
    subject_token: str,
    timeout_seconds: float = 5.0,
) -> str:
    token_response = await exchange_token_for_own_client(
        subject_token=subject_token,
        timeout_seconds=timeout_seconds,
    )
    return token_response["access_token"]
