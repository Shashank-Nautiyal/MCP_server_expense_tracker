# Expense Tracker MCP Server

A remote [MCP](https://modelcontextprotocol.io) server that lets an AI assistant such as Claude track your expenses. Every user signs in with GitHub and only ever sees their own data.

Built with FastMCP, async SQLAlchemy and PostgreSQL, and deployed on Railway.

## Features

- **Five tools:** add, update, delete and list expenses, plus a spending summary by category.
- **One resource:** `expense://categories` gives the assistant the list of valid categories and subcategories.
- **GitHub login (OAuth):** users authenticate through FastMCP's `GitHubProvider`.
- **Per-user data:** every expense belongs to a GitHub user, and every query is filtered by that user.
- **Fully async:** async SQLAlchemy with PostgreSQL.
- **Layered code:** thin MCP tools on top of a service layer that holds the business rules.

## Tech stack

| Area | Choice |
|---|---|
| Language | Python 3.14 |
| MCP framework | FastMCP 4.x |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.x (async) with asyncpg / psycopg |
| Settings | pydantic-settings |
| Package manager | uv |
| Hosting | Railway |

## Project structure

```
MCP_server_expense_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py            # creates and starts the FastMCP server
│   ├── config.py          # environment settings
│   ├── auth.py            # GitHub login and current_user_id()
│   ├── database.py        # async engine, sessions, table creation
│   ├── model.py           # SQLAlchemy Expense model
│   ├── tools.py           # MCP tools (thin layer)
│   ├── services/
│   │   └── expenses.py    # business logic, always scoped to a user
│   ├── resources/
│   │   └── categories.py  # expense://categories resource
│   └── data/
│       └── categories.json
├── pyproject.toml
├── .env.example
└── .gitignore
```

## How it works

1. A client (for example Claude) connects to `/mcp`. FastMCP starts the GitHub OAuth flow, and the user signs in with GitHub.
2. For each tool call, `current_user_id()` reads the user's id from the verified login token. The user id is **never** a tool argument, because a client could send any value.
3. The tool opens a database session and calls a function in `services/expenses.py`.
4. Every query in the service layer filters by `user_id`. Update and delete return "not found" for rows that belong to someone else, so other users' ids can't be probed.

## Tools

Dates use the format `YYYY-MM-DD`. Use category names from the `expense://categories` resource.

| Tool | Arguments | What it does |
|---|---|---|
| `add_expense` | `date`, `amount`, `category`, `subcategory=""`, `note=""` | Adds an expense for the current user. |
| `update_expense` | `expense_id`, optional `amount`, `category`, `subcategory`, `note` | Changes only the fields you pass. |
| `delete_expense` | `expense_id` | Deletes one of your expenses. |
| `list_expenses` | `start_date`, `end_date` | Lists your expenses in an inclusive date range. |
| `summarize` | `start_date`, `end_date`, optional `category` | Totals your spending per category. |

## Environment variables

Copy `.env.example` to `.env` for local development. On a host such as Railway, set these as environment variables instead.

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async PostgreSQL URL, for example `postgresql+asyncpg://user:password@host:5432/dbname` (`postgresql+psycopg://` also works). |
| `GITHUB_CLIENT_ID` | Client ID of your GitHub OAuth App. |
| `GITHUB_CLIENT_SECRET` | Client secret of your GitHub OAuth App. |
| `BASE_URL` | Public URL of the server, with `https://` and no trailing slash or `/mcp`. Locally: `http://localhost:8000`. |
| `JWT_SIGNING_KEY` | Long random string used to sign the server's tokens. |

Generate a signing key with:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Never commit `.env`. It is listed in `.gitignore`.

## Run locally

**Prerequisites:** Python 3.14, [uv](https://docs.astral.sh/uv/), a running PostgreSQL database, and a GitHub account.

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Create a GitHub OAuth App** at <https://github.com/settings/developers> (OAuth Apps, then New OAuth App):
   - Homepage URL: `http://localhost:8000`
   - Redirect URI: `http://localhost:8000/auth/callback`

   Copy the Client ID, then generate and copy a Client Secret.

3. **Create your `.env`** from `.env.example` and fill in the five variables above.

4. **Start the server** from the project root:

   ```bash
   uv run python -m app.main
   ```

   Tables are created automatically on startup.

5. **Try it** with a small client script. The first run opens GitHub in your browser:

   ```python
   import asyncio
   from fastmcp import Client

   async def main():
       async with Client("http://localhost:8000/mcp", auth="oauth") as client:
           print(await client.list_tools())

   asyncio.run(main())
   ```

## Deploy to Railway

1. Create a project with a **PostgreSQL** service and a service for this repo (deploy from GitHub).
2. On the app service, open **Settings → Networking** and click **Generate Domain**.
3. In your GitHub OAuth App, add this redirect URI: `https://<your-domain>/auth/callback`
4. On the app service, set the variables from the table above:
   - `BASE_URL` = `https://<your-domain>`
   - `DATABASE_URL` = `postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}`
   - plus `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` and a new `JWT_SIGNING_KEY`
5. Set the start command (**Settings → Deploy**) to `python -m app.main`. The server reads Railway's `PORT` variable automatically.
6. Push to GitHub and check the deploy logs for `Uvicorn running on ...`.

## Connect from Claude

Add the server as a custom connector with the full MCP URL, including `/mcp`:

```
https://<your-domain>/mcp
```

Approve the GitHub sign-in when asked. Then try prompts like "add a 50 rupee tea expense for today" or "summarize my spending this month".

## Known limitations

- **Logins reset after a redeploy.** Token storage is not persistent. Users may need to sign in again. A persistent store such as Redis fixes this (see the FastMCP OAuth proxy docs).
- **No database migrations.** Tables are created with `create_all`, which doesn't change existing tables. Adding a column to a live database needs a manual `ALTER TABLE` or a migration tool such as Alembic.
- **Anyone with a GitHub account can sign in.** There is no allowlist of users yet.

## Security notes

- Secrets live only in environment variables, never in the repository.
- The user id always comes from the verified token, never from tool input.
- Rows are filtered by `user_id` in every query, and ownership is checked again on update and delete.



[![M8ven Score](https://m8ven.ai/badge/mcp/shashank-nautiyal-mcp-server-expense-tracker-8qoovn?v=cca63ec295cf6afa32af2d583b0e9c1b)](https://m8ven.ai/mcp/shashank-nautiyal-mcp-server-expense-tracker-8qoovn?s=readme)

# Expense Tracker MCP Server

[![M8ven Score](https://m8ven.ai/badge/mcp/shashank-nautiyal/mcp_server_expense_tracker)](https://m8ven.ai/mcp/shashank-nautiyal/mcp_server_expense_tracker?s=readme)
