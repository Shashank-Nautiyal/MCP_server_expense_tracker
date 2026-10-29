from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from app.auth import current_user_id
from app.database import session_Local
from app.services import util as svc
from app.tools.annotations import READ


async def summarize(start_date: str, end_date: str, category: str | None = None):
    """Total the current user's spending per category between two dates (YYYY-MM-DD).

    Pass category to limit the summary to one category.
    """
    user_id = current_user_id()
    async with session_Local() as db:
        try:
            return await svc.summarize_expenses(
                db, user_id, start_date, end_date, category
            )
        except ValueError as e:
            raise ToolError(str(e)) from e


def register(mcp: FastMCP) -> None:
    """Register the report tools. Called from app/tools/__init__.py."""
    mcp.tool(annotations=READ)(summarize)
