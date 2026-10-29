from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from app.auth import current_user_id
from app.database import session_Local
from app.services import util as svc
from app.tools.annotations import ADD, CHANGE, READ


async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
):
    """Add a new expense for the current user.

    date uses the format YYYY-MM-DD. Use category and subcategory names from
    the expense://categories resource.
    """
    user_id = current_user_id()
    async with session_Local() as db:
        try:
            expense = await svc.add_expense(
                db,
                user_id,
                date=date,
                amount=amount,
                category=category,
                subcategory=subcategory,
                note=note,
            )
        except ValueError as e:
            raise ToolError(str(e)) from e
    return {"status": "ok", "id": expense["id"]}


async def update_expense(
    expense_id: int,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    note: str | None = None,
):
    """Update one of the current user's expenses. Only the fields you pass change."""
    user_id = current_user_id()
    async with session_Local() as db:
        try:
            expense = await svc.update_expense(
                db,
                user_id,
                expense_id,
                amount=amount,
                category=category,
                subcategory=subcategory,
                note=note,
            )
        except svc.ExpenseNotFoundError:
            return {"status": "error", "message": "Expense not found"}
    return {"status": "ok", **expense}


async def delete_expense(expense_id: int):
    """Delete one of the current user's expenses by its id."""
    user_id = current_user_id()
    async with session_Local() as db:
        try:
            await svc.delete_expense(db, user_id, expense_id)
        except svc.ExpenseNotFoundError:
            return {"status": "error", "message": "Expense not found"}
    return {
        "status": "ok",
        "message": "Expense deleted successfully",
        "id": expense_id,
    }


async def list_expenses(start_date: str, end_date: str):
    """List the current user's expenses between two dates (inclusive, YYYY-MM-DD)."""
    user_id = current_user_id()
    async with session_Local() as db:
        try:
            return await svc.list_expenses(db, user_id, start_date, end_date)
        except ValueError as e:
            raise ToolError(str(e)) from e


def register(mcp: FastMCP) -> None:
    """Register the expense tools. Called from app/tools/__init__.py."""
    mcp.tool(annotations=ADD)(add_expense)
    mcp.tool(annotations=CHANGE)(update_expense)
    mcp.tool(annotations=CHANGE)(delete_expense)
    mcp.tool(annotations=READ)(list_expenses)
