import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastmcp import FastMCP
from sqlalchemy import func, select

from database import init_db, session_Local
from model import Expense



CATEGORIES_PATH = Path(__file__).resolve().parent / "categories.json"


@asynccontextmanager
async def lifespan(server):
    await init_db()
    yield


mcp = FastMCP("ExpenseTracker", lifespan=lifespan)


@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
):
    """Add a new expense to the database."""
    async with session_Local() as db:
        expense = Expense(
            date=date,
            amount=amount,
            category=category,
            subcategory=subcategory,
            note=note,
        )
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return {"status": "ok", "id": expense.id}


@mcp.tool()
async def update_expense(
    expense_id: int,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    note: str | None = None,
):
    """Update an existing expense."""
    async with session_Local() as db:
        expense = await db.get(Expense, expense_id)

        if expense is None:
            return {"status": "error", "message": "Expense not found"}

        if amount is not None:
            expense.amount = amount
        if category is not None:
            expense.category = category
        if subcategory is not None:
            expense.subcategory = subcategory
        if note is not None:
            expense.note = note

        await db.commit()
        await db.refresh(expense)

        return {
            "status": "ok",
            "id": expense.id,
            "amount": str(expense.amount),
            "category": expense.category,
            "subcategory": expense.subcategory,
            "note": expense.note,
        }


@mcp.tool()
async def delete_expense(expense_id: int):
    """Delete an expense by its id."""
    async with session_Local() as db:
        expense = await db.get(Expense, expense_id)

        if expense is None:
            return {"status": "error", "message": "Expense not found"}

        await db.delete(expense)
        await db.commit()
        return {
            "status": "ok",
            "message": "Expense deleted successfully",
            "id": expense_id,
        }


@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    """List expenses within an inclusive date range."""
    async with session_Local() as db:
        result = await db.execute(
            select(Expense)
            .where(Expense.date >= start_date, Expense.date <= end_date)
            .order_by(Expense.date.asc(), Expense.id.asc())
        )
        expenses = result.scalars().all()

        return [
            {
                "id": e.id,
                "date": str(e.date),
                "amount": str(e.amount),
                "category": e.category,
                "subcategory": e.subcategory,
                "note": e.note,
            }
            for e in expenses
        ]


@mcp.tool()
async def summarize(start_date: str, end_date: str, category: str | None = None):
    """Summarize expenses by category within an inclusive date range."""
    stmt = (
        select(Expense.category, func.sum(Expense.amount).label("total_amount"))
        .where(Expense.date >= start_date, Expense.date <= end_date)
    )

    if category:
        stmt = stmt.where(Expense.category == category)

    stmt = stmt.group_by(Expense.category).order_by(Expense.category.asc())

    async with session_Local() as db:
        result = await db.execute(stmt)
        rows = result.all()

    return [
        {"category": row.category, "total_amount": float(row.total_amount)}
        for row in rows
    ]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    return CATEGORIES_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )