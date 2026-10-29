"""MCP tool hints shared by every tool.

All four hints are set explicitly on each tool. They are advisory for clients;
the real protection is the user_id filter in every query (see app/services).
"""

# Adds a new row. Calling it twice adds two rows, so it is not idempotent.
ADD = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
}

# Overwrites or removes existing data. Repeating the same call has no extra effect.
CHANGE = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}

# Only reads data.
READ = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}
