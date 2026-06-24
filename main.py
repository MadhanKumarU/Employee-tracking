# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from typing import Dict, Optional
from datetime import datetime, date
import os

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Date,
    TIMESTAMP, select, insert, update, text
)
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError

# -------------------------
# DB CONFIG
# -------------------------
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "Praveen@2412")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "employee_monitoring")

DATABASE_URL = URL.create(
    "mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

# -------------------------
# TABLES
# -------------------------
employees = Table(
    "employees", metadata,
    Column("id", Integer, primary_key=True),
    Column("employee_code", String(50), unique=True),
    Column("name", String(100)),
    Column("department", String(100)),
    Column("role", String(50)),
    Column("system_name", String(150)),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
)

apps = Table(
    "apps", metadata,
    Column("id", Integer, primary_key=True),
    Column("app_name", String(200), unique=True),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
)

app_usage = Table(
    "app_usage", metadata,
    Column("id", Integer, primary_key=True),
    Column("employee_id", Integer),
    Column("app_id", Integer),
    Column("date", Date),
    Column("total_seconds", Integer, default=0),
)

# -------------------------
# MODELS
# -------------------------
class IngestPayload(BaseModel):
    employee_code: str
    system_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    apps: Dict[str, int]


app = FastAPI(title="Employee Monitoring API")
@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/dashboard/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response
static_dir = os.path.join(os.path.dirname(__file__), "static")
dashboard_dir = os.path.join(static_dir, "dashboard")

# Mount /static → backend/static/
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve /dashboard → index.html
@app.get("/dashboard", include_in_schema=False)
def dashboard_index():
    index_path = os.path.join(dashboard_dir, "index.html")
    return FileResponse(
        index_path,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

# -------------------------
# HELPERS
# -------------------------
def get_or_create_employee(conn, employee_code, system_name=None):
    row = conn.execute(
        select(employees).where(employees.c.employee_code == employee_code)
    ).fetchone()

    if row:
        if system_name and row._mapping["system_name"] != system_name:
            conn.execute(
                update(employees)
                .where(employees.c.id == row._mapping["id"])
                .values(system_name=system_name)
            )
        return row._mapping["id"]

    res = conn.execute(
        insert(employees).values(employee_code=employee_code, system_name=system_name)
    )
    return res.lastrowid


def get_or_create_app(conn, app_name):
    row = conn.execute(
        select(apps).where(apps.c.app_name == app_name)
    ).fetchone()

    if row:
        return row._mapping["id"]

    try:
        res = conn.execute(insert(apps).values(app_name=app_name))
        return res.lastrowid
    except IntegrityError:
        row = conn.execute(
            select(apps).where(apps.c.app_name == app_name)
        ).fetchone()
        return row._mapping["id"]

# -------------------------
# INGEST ENDPOINT
# -------------------------
@app.post("/ingest", status_code=201)
def ingest(payload: IngestPayload):
    ts = payload.timestamp or datetime.utcnow()
    report_date = ts.date()

    with engine.begin() as conn:
        emp_id = get_or_create_employee(conn, payload.employee_code, payload.system_name)
        updated = []

        for app_name, seconds in payload.apps.items():
            if seconds <= 0:
                continue
            if app_name == "__IDLE_TIME__":
                app_name = "Idle Time"

            app_id = get_or_create_app(conn, app_name)

            existing = conn.execute(
                select(app_usage)
                .where(app_usage.c.employee_id == emp_id)
                .where(app_usage.c.app_id == app_id)
                .where(app_usage.c.date == report_date)
            ).fetchone()

            if existing:
                new_total = existing._mapping["total_seconds"] + int(seconds)
                conn.execute(
                    update(app_usage)
                    .where(app_usage.c.id == existing._mapping["id"])
                    .values(total_seconds=new_total)
                )
            else:
                conn.execute(
                    insert(app_usage).values(
                        employee_id=emp_id,
                        app_id=app_id,
                        date=report_date,
                        total_seconds=int(seconds),
                    )
                )

            updated.append({"app": app_name, "added_seconds": int(seconds)})

    return {"status": "ok", "updated": updated}

# -------------------------
# EMPLOYEES LIST
# -------------------------
@app.get("/employees")
def list_employees():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM employees")).fetchall()
        return [dict(row._mapping) for row in rows]

# -------------------------
# EMPLOYEE USAGE
# -------------------------
@app.get("/usage/{employee_code}")
def usage(employee_code: str, date_str: Optional[str] = None):
    use_date = date_str or str(date.today())

    with engine.connect() as conn:
        emp = conn.execute(
            select(employees).where(employees.c.employee_code == employee_code)
        ).fetchone()

        if not emp:
            raise HTTPException(404, "Employee not found")

        rows = conn.execute(
            select(app_usage.c.total_seconds, apps.c.app_name)
            .select_from(app_usage.join(apps, app_usage.c.app_id == apps.c.id))
            .where(app_usage.c.employee_id == emp._mapping["id"])
            .where(app_usage.c.date == use_date)
        ).fetchall()

        return {
            "employee_code": employee_code,
            "date": use_date,
            "apps": [
                {"app": r._mapping["app_name"], "total_seconds": r._mapping["total_seconds"]}
                for r in rows
            ],
        }

# -------------------------
# LIVE DASHBOARD
# -------------------------
@app.get("/live")
def live():
    with engine.connect() as conn:
        rows = conn.execute(
            select(employees.c.employee_code, apps.c.app_name, app_usage.c.total_seconds)
            .select_from(
                app_usage.join(employees, app_usage.c.employee_id == employees.c.id)
                .join(apps, app_usage.c.app_id == apps.c.id)
            )
            .where(app_usage.c.date == date.today())
        ).fetchall()

        out = {}
        for r in rows:
            emp = r._mapping["employee_code"]
            out.setdefault(emp, []).append(
                {"app": r._mapping["app_name"], "total_seconds": r._mapping["total_seconds"]}
            )
        return out

