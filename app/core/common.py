import os

CLIEND_ID : str = os.getenv("CLIENT_ID")
KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "default_realm")
KEYCLOAK_ISSUER: str = os.getenv(
    "KEYCLOAK_ISSUER",
    f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}",
)
KEYCLOAK_TOKEN_ENDPOINT: str = (
    f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token"
)
KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "").strip()
