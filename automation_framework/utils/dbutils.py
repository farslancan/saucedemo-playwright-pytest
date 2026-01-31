import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union

from automation_framework.config import global_config as gc

QueryResult = Union[list[tuple], list[dict[str, Any]], int]


def _resolve_user(default: Optional[str]) -> str:
    return default or getattr(gc, "DB_USERNAME", getattr(gc, "DB_USER", ""))


def _resolve_password(default: Optional[str]) -> str:
    return default or getattr(gc, "DB_PASSWORD", "")


def create_db_connection(
    *,
    database: str,
    user: Optional[str] = gc.DB_USERNAME,
    password: Optional[str] = gc.DB_PASSWORD,
    host: Optional[str] = gc.DB_HOST,
    port: Optional[Union[int, str]] = gc.DB_PORT,
    autocommit: bool = False,
    sslmode: Optional[str] = None,
) -> Any:
    """
    Establish a MySQL/MariaDB connection using host/port from global_config by default.
    """
    try:
        import pymysql  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyMySQL is required to create DB connections") from exc

    resolved_port = int(port or getattr(gc, "DB_PORT", 3306))
    resolved_ssl_mode = (sslmode or getattr(gc, "DB_SSL_MODE", "") or "").lower()
    if resolved_ssl_mode in ("disable", "off", ""):
        ssl_opts = None
    elif resolved_ssl_mode in ("require", "preferred", "verify_ca", "verify_full"):
        ssl_opts = {}
    else:
        raise ValueError(f"Unsupported DB_SSL_MODE/sslmode value: {sslmode}")

    conn = pymysql.connect(
        host=host or gc.DB_HOST,
        port=resolved_port,
        user=user,
        password=_resolve_password(password),
        database=database,
        autocommit=autocommit,
        ssl=ssl_opts,
    )
    return conn


@contextmanager
def db_connection(**kwargs) -> Generator[Any, None, None]:
    """
    Context manager wrapper for create_db_connection that closes the connection.
    Usage:
        with db_connection(database="mydb") as conn:
            ...
    """
    conn = create_db_connection(**kwargs)
    try:
        yield conn
    finally:
        conn.close()


def _run_query(
    conn: Any,
    query: str,
    params: Optional[Any] = None,
    *,
    fetch: bool = False,
    commit: bool = False,
    cursorclass: Optional[Any] = None,
) -> QueryResult:
    with conn.cursor(cursorclass) if cursorclass else conn.cursor() as cur:
        if params is None:
            cur.execute(query)
        else:
            cur.execute(query, params)

        # Fetch results if requested or if the statement returns rows.
        if fetch or cur.description:
            rows = cur.fetchall()
            if commit and not conn.get_autocommit():
                conn.commit()
            return rows

        if commit and not conn.get_autocommit():
            conn.commit()
        return cur.rowcount


def _split_sql_statements(sql_text: str, delimiter: str = ";") -> list[str]:
    """
    Split SQL text into individual statements while ignoring comments.
    """
    statements: list[str] = []
    current_parts: list[str] = []
    in_multiline_comment = False

    for raw_line in sql_text.splitlines():
        line = raw_line

        if in_multiline_comment:
            if "*/" in line:
                line = line.split("*/", 1)[1]
                in_multiline_comment = False
            else:
                continue

        if "/*" in line:
            before, after = line.split("/*", 1)
            if "*/" in after:
                after = after.split("*/", 1)[1]
                line = before + after
            else:
                line = before
                in_multiline_comment = True

        for token in ("--", "#"):
            if token in line:
                line = line.split(token, 1)[0]

        cleaned = line.strip()
        if not cleaned:
            continue

        current_parts.append(cleaned)

        if cleaned.endswith(delimiter):
            current_parts[-1] = current_parts[-1][: -len(delimiter)].rstrip()
            statement = " ".join(current_parts).strip()
            if statement:
                statements.append(statement)
            current_parts = []

    leftover = " ".join(current_parts).strip()
    if leftover:
        statements.append(leftover)

    return statements



def execute_select(
    conn: Any,
    query: str,
    params: Optional[Any] = None,
    *,
    return_dict: bool = False,
) -> Union[list[tuple], list[dict[str, Any]]]:
    """
    Execute a SELECT query and return all rows.
    return_dict=True uses DictCursor to return list of dictionaries.
    """
    if return_dict:
        try:
            from pymysql.cursors import DictCursor  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PyMySQL is required to create DB connections") from exc
        return _run_query(
            conn, query, params, fetch=True, cursorclass=DictCursor
        )  # type: ignore[return-value]

    return _run_query(conn, query, params, fetch=True)  # type: ignore[return-value]


def execute_insert(
    conn: Any,
    query: str,
    params: Optional[Any] = None,
    *,
    commit: bool = True,
) -> QueryResult:
    """
    Execute an INSERT query. Returns fetched rows if the statement includes RETURNING,
    otherwise the affected row count.
    """
    return _run_query(conn, query, params, commit=commit)


def execute_update(
    conn: Any,
    query: str,
    params: Optional[Any] = None,
    *,
    commit: bool = True,
) -> QueryResult:
    """
    Execute an UPDATE query. Returns fetched rows if the statement includes RETURNING,
    otherwise the affected row count.
    """
    return _run_query(conn, query, params, commit=commit)


def execute_delete(
    conn: Any,
    query: str,
    params: Optional[Any] = None,
    *,
    commit: bool = True,
) -> QueryResult:
    """
    Execute a DELETE query. Returns fetched rows if the statement includes RETURNING,
    otherwise the affected row count.
    """
    return _run_query(conn, query, params, commit=commit)


def execute_truncate(
    conn: Any,
    table_name: str,
    *,
    force_truncate: bool = False,
    commit: bool = True,
) -> QueryResult:
    """
    Execute a TRUNCATE query on the specified table.

    Args:
        conn: Open DB connection.
        table_name: The name of the table to truncate.
        force_truncate: If True, disables foreign key checks before truncating
                        and re-enables them afterward.
        commit: If True (default), commits the transaction.
    """
    if force_truncate:
        _run_query(conn, "SET FOREIGN_KEY_CHECKS = 0;", commit=False)

    try:
        result = _run_query(conn, f"TRUNCATE TABLE {table_name};", commit=commit)
    finally:
        if force_truncate:
            _run_query(conn, "SET FOREIGN_KEY_CHECKS = 1;", commit=commit)

    return result