import asyncio
import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP

import app.model  
from app.auth import auth
from app.database import init_db
from app.resource import register_resources
from app.tools import register_tools

@asynccontextmanager
async def lifespan(server):
    await init_db()  
    yield


mcp = FastMCP("ExpenseTracker", auth=auth, lifespan=lifespan)
register_tools(mcp)
register_resources(mcp)


def main() -> None:
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),  
    )


if __name__ == "__main__":
    main()