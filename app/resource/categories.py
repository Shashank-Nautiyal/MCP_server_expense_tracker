
from pathlib import Path

from fastmcp import FastMCP

CATEGORIES_PATH = Path(__file__).resolve().parent.parent / "data" / "categories.json"


def categories() -> str:
    # Read fresh each time so edits don't need a restart
    return CATEGORIES_PATH.read_text(encoding="utf-8")


def register(mcp: FastMCP) -> None:
    mcp.resource("expense://categories", mime_type="application/json")(categories)