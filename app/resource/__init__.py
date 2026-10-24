from fastmcp import FastMCP

from app.resource import categories


def register_resources(mcp: FastMCP) -> None:
    """Register every resource on the server. Called once from app/main.py."""
    categories.register(mcp)