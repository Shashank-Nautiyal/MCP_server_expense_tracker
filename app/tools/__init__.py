from fastmcp import FastMCP

from app.tools import expenses, reports


def register_tools(mcp: FastMCP) -> None:
    expenses.register(mcp)
    reports.register(mcp)
   