from fastmcp.server.auth.providers.github import GitHubProvider
from app.config import settings

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token

auth = GitHubProvider(
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    base_url=settings.base_url,
    jwt_signing_key=settings.jwt_signing_key,
)

def current_user_id() -> str:
    """Return the authenticated user's ID."""
    token = get_access_token()

    if token is None:
        raise ToolError("Not authenticated")

    user_id = token.claims.get("sub") or token.claims.get("login")

    if not user_id:
        raise ToolError("Could not identify the user")

    return str(user_id)