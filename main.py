from database import session_Local
from fastmcp import FastMCP
from model import Expense
from database import engine,Base
from sqlalchemy import func


CATEGORIES_PATH="D:\\Ai-engineer-learning\\Mcp_learning\\MCP_server\\expense_tracker_mcp_server\\categories.json"
Base.metadata.create_all(bind=engine)
mcp=FastMCP("ExepenseTracker")

@mcp.tool()
def add_expense(date:str,amount:float,category:str,subcategory:str="",note:str=""):
    """add new expense to the database"""
    with session_Local() as db:
        expense=Expense(date=date,
                        amount=amount,
                        category=category,
                        subcategory=subcategory,
                        note=note)
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return {"status": "ok", "id": expense.id}


@mcp.tool()
def update_expense(
    expense_id: int,
    amount: float = None,
    category: str = None,
    subcategory: str = None,
    note: str = None
):
    """Update an existing expense."""

    with session_Local() as db:
        expense = db.query(Expense).filter(
            Expense.id == expense_id
        ).first()

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

        db.commit()
        db.refresh(expense)

        return {
            "status": "ok",
            "id": expense.id,
            "amount": str(expense.amount),
            "category": expense.category,
            "subcategory": expense.subcategory,
            "note": expense.note
        }

    
@mcp.tool()
def delete_expense(expense_id:int):
    """delete by its expense id """
    with session_Local() as db:
        expense=db.query(Expense).filter(Expense.id==expense_id).first()
        if not expense:
            return {"status": "error", "message": "Expense not found"}

        db.delete(expense)
        db.commit()
        return {
            "status": "ok",
            "message": "Expense deleted successfully",
            "id": expense_id
        }

@mcp.tool()
def list_expenses(start_date:str,end_date:str):
    """List all expenses from the database."""
    with session_Local() as db:
        expenses=db.query(Expense).filter(Expense.date>=start_date,
                                          Expense.date<=end_date
                                          ).order_by(Expense.date.asc(),Expense.id.asc()).all()
        return [
            {
                "id": expense.id,
                "date": str(expense.date),
                "amount": str(expense.amount),
                "category": expense.category,
                "subcategory": expense.subcategory,
                "note": expense.note
            }
            for expense in expenses
        ]

@mcp.tool()
def summarize(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category within an inclusive date range."""

    with session_Local() as db:
        query = (
            db.query(
                Expense.category,
                func.sum(Expense.amount).label("total_amount")
            )
            .filter(
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        )

        if category:
            query = query.filter(Expense.category == category)

        results = (
            query
            .group_by(Expense.category)
            .order_by(Expense.category.asc())
            .all()
        )

        return [
            {
                "category": row.category,
                "total_amount": float(row.total_amount)
            }
            for row in results
        ]




@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
     mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )
