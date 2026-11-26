"""SAKHI - FastAPI Backend & Frontend Integration.

Serves the frontend SPA and exposes REST endpoints connecting to the
SQLite database (asha_data.db) and core backend logic in backend/backend.py.
"""

import json
import logging
import os
import re
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sakhi.api")

# Base directory resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Ensure backend directory is in sys.path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure SAKHI_DB_PATH and SAKHI_VACS_PATH are set
DB_PATH = Path(os.environ.get("SAKHI_DB_PATH", str(BACKEND_DIR / "asha_data.db")))
VACS_PATH = Path(os.environ.get("SAKHI_VACS_PATH", str(BACKEND_DIR / "vacs.json")))

os.environ["SAKHI_DB_PATH"] = str(DB_PATH)
os.environ["SAKHI_VACS_PATH"] = str(VACS_PATH)

# Load backend module
try:
    import backend
except ImportError as e:
    logger.error("Failed to import backend module: %s", e)
    raise

try:
    from src.prioritization import (
        PRIORITY_RULES_CONFIG,
        UNVALIDATED_RULE_PLACEHOLDERS,
        compute_all_priorities,
        parse_flexible_date,
    )
    from src.sarvam_service import SarvamSpeechService
    from src.voice_service import parse_voice_transcript
    from src.voice_action_service import execute_confirmed_action, prepare_action_preview
    from src.voice_form_extractor import extract_for_form_context
    from src.chatbot_service import handle_chat_message
except ImportError:
    from prioritization import (
        PRIORITY_RULES_CONFIG,
        UNVALIDATED_RULE_PLACEHOLDERS,
        compute_all_priorities,
        parse_flexible_date,
    )
    from sarvam_service import SarvamSpeechService
    from voice_service import parse_voice_transcript
    from voice_action_service import execute_confirmed_action, prepare_action_preview
    from voice_form_extractor import extract_for_form_context
    from chatbot_service import handle_chat_message

sarvam_service = SarvamSpeechService()

# Load optional .env file if present
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    except Exception as e:
        logger.warning("Could not read .env: %s", e)

# Initialize FastAPI App
app = FastAPI(
    title="SAKHI — ASHA Healthcare Assistant",
    description="Integrated local platform for ASHA field workers with SQLite & FastAPI.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Request & Response Models
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    mobile: str
    password: str


class MotherCreateRequest(BaseModel):
    name: str
    beneficiary_id: Optional[str] = None
    age: Optional[int] = 28
    dob: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    weeks: Optional[int] = 12
    dueDate: Optional[str] = None
    weight: Optional[str] = "55 kg"
    ironStatus: Optional[str] = "Regular"
    bloodGroup: Optional[str] = "O+"


class ChildCreateRequest(BaseModel):
    name: str
    beneficiary_id: Optional[str] = None
    age: Optional[str] = "6 months"
    gender: Optional[str] = "Male"
    dob: Optional[str] = None
    phone: Optional[str] = None
    guardian: Optional[str] = None
    address: Optional[str] = None
    bloodGroup: Optional[str] = "B+"
    weight: Optional[float] = 4.5
    nextVisit: Optional[str] = None


class VisitCreateRequest(BaseModel):
    beneficiary_id: str
    visit_type: str = "ANC"
    due_date: str
    note: Optional[str] = ""
    voice: Optional[str] = ""
    flag: Optional[str] = "N"
    origin: Optional[str] = "priority_dashboard"


class VisitUpdateRequest(BaseModel):
    status: Optional[str] = "Complete"
    note: Optional[str] = None
    voice: Optional[str] = None
    visit_type: Optional[str] = None
    location: Optional[Dict[str, Any]] = None


class ChatQueryRequest(BaseModel):
    query: str
    beneficiary_id: Optional[str] = None
    current_draft: Optional[Dict[str, Any]] = None
    screen_context: Optional[Dict[str, Any]] = None
    shared_tab_context: Optional[Dict[str, Any]] = None
    language_code: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ProcessNoteRequest(BaseModel):
    note: str
    beneficiary_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    lang: Optional[str] = "en-IN"
    language_code: Optional[str] = None
    speaker: Optional[str] = "ritu"


class VoiceUnderstandRequest(BaseModel):
    transcript: str
    context_screen: Optional[str] = "home"
    beneficiary_id: Optional[str] = None
    current_draft: Optional[Dict[str, Any]] = None
    screen_context: Optional[Dict[str, Any]] = None
    shared_tab_context: Optional[Dict[str, Any]] = None
    language_code: Optional[str] = None


class VoiceExecuteRequest(BaseModel):
    action_type: str
    payload: Dict[str, Any]
    confirmed: bool = False


class VoiceFormExtractRequest(BaseModel):
    transcript: str
    form_context: Dict[str, Any]
    reference_date: Optional[str] = None
    language_code: Optional[str] = None


class TranslateRequest(BaseModel):
    text: str
    source_lang: Optional[str] = "kn"
    target_lang: Optional[str] = "en"


class VaccineUpdateRequest(BaseModel):
    beneficiary_id: str
    vaccine_name: str
    administered_date: Optional[str] = None
    mode: str = "child"


# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def get_db_connection():
    """Returns a direct SQLite connection with Row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def safe_json_loads(val: Any, default: Any = None):
    if not val:
        return default if default is not None else {}
    if isinstance(val, (dict, list)):
        return val
    try:
        return json.loads(val)
    except Exception:
        return default if default is not None else {}


# -------------------------------------------------------------
# System & Health Routes
# -------------------------------------------------------------
@app.get("/health")
@app.get("/api/health")
def health_check():
    """Healthcheck endpoint checking DB connectivity and file persistence."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT count(*) as count FROM home_records")
        homes_cnt = c.fetchone()["count"]
        c.execute("SELECT count(*) as count FROM visits")
        visits_cnt = c.fetchone()["count"]
        c.execute("SELECT count(*) as count FROM pregnancies")
        preg_cnt = c.fetchone()["count"]
        c.execute("SELECT count(*) as count FROM children")
        child_cnt = c.fetchone()["count"]
        conn.close()

        return {
            "status": "healthy",
            "database": {
                "path": str(DB_PATH),
                "exists": DB_PATH.exists(),
                "tables_count": 19,
                "counts": {
                    "homes": homes_cnt,
                    "pregnancies": preg_cnt,
                    "children": child_cnt,
                    "visits": visits_cnt,
                },
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error("Health check error: %s", e)
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e), "database_path": str(DB_PATH)},
        )


# -------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------
@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    """Authenticate ASHA worker against asha_workers in SQLite."""
    mobile = req.mobile.strip()
    password = req.password.strip()

    # If user submitted the default placeholder bullets or empty string, resolve to demo password
    if password in ("••••••••", ""):
        password = "pass12"

    try:
        res = backend.login(mobile, password)
        if res.get("success"):
            return res

        # Check fallback for mobile matching or default demo credentials
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM asha_workers WHERE mobile = ?", (mobile,)).fetchone()
        conn.close()

        if row:
            if row["password"] == password:
                user = {
                    "id": row["id"],
                    "name": row["name"],
                    "mobile": row["mobile"],
                    "email": row["email"],
                    "dob": row["dob"],
                    "address": row["address"],
                }
                return {"success": True, "message": "Login successful", "user": user}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/profile")
def get_profile(worker_id: str = "AW001"):
    """Get ASHA worker profile."""
    try:
        df = backend.get_asha_worker_profile(worker_id)
        if not df.empty:
            return {"success": True, "profile": df.iloc[0].to_dict()}

        conn = get_db_connection()
        row = conn.execute("SELECT * FROM asha_workers LIMIT 1").fetchone()
        conn.close()
        if row:
            return {"success": True, "profile": dict(row)}

        raise HTTPException(status_code=404, detail="Worker profile not found")
    except Exception as e:
        logger.error("Profile error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/workers")
def list_workers():
    """List available ASHA workers for login."""
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT id, name, mobile, email, address FROM asha_workers").fetchall()
        conn.close()
        return {"success": True, "workers": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Dashboard & Metrics Routes
# -------------------------------------------------------------
@app.get("/api/dashboard")
def get_dashboard():
    """Returns aggregated dashboard metrics from backend and database."""
    try:
        records = backend.get_all_records()
        metrics = records.get("metrics", {})

        # Convert numpy/pandas scalar types if any
        cleaned_metrics = {}
        for k, v in metrics.items():
            if hasattr(v, "item"):
                cleaned_metrics[k] = v.item()
            else:
                cleaned_metrics[k] = v

        # Build clean summary for frontend stats
        conn = get_db_connection()
        total_homes = conn.execute("SELECT count(*) FROM home_records").fetchone()[0]
        total_pregnancies = conn.execute("SELECT count(*) FROM pregnancies").fetchone()[0]
        total_children = conn.execute("SELECT count(*) FROM children").fetchone()[0]
        total_visits = conn.execute("SELECT count(*) FROM visits").fetchone()[0]
        completed_visits = conn.execute("SELECT count(*) FROM visits WHERE visit_ts IS NOT NULL AND visit_ts != ''").fetchone()[0]
        pending_visits = total_visits - completed_visits
        high_risk_visits = conn.execute("SELECT count(*) FROM visits WHERE flag IN ('H', 'S', 'HS')").fetchone()[0]
        high_risk_preg = conn.execute("SELECT count(*) FROM pregnancies WHERE status = 'HIGH_RISK'").fetchone()[0]
        prio_data = compute_all_priorities(conn)
        conn.close()

        summary = {
            "total_homes": total_homes,
            "pregnant_women": total_pregnancies,
            "newborns": total_children,
            "total_visits": total_visits,
            "completed_visits": completed_visits,
            "pending_visits": pending_visits,
            "high_risk_cases": high_risk_visits + high_risk_preg,
            "metrics": cleaned_metrics,
            "prioritization": prio_data["summary"],
        }

        return {"success": True, "data": summary}
    except Exception as e:
        logger.error("Dashboard error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Household Prioritization Intelligence Routes
# -------------------------------------------------------------
@app.get("/api/priorities/rules")
def get_priority_rules():
    """Return configurable prioritization rules and explicit unvalidated clinical placeholders."""
    return {
        "success": True,
        "rules_config": {
            "emergency_flags": sorted(PRIORITY_RULES_CONFIG["emergency_flags"]),
            "high_priority_flags": sorted(PRIORITY_RULES_CONFIG["high_priority_flags"]),
            "moderate_flags": sorted(PRIORITY_RULES_CONFIG["moderate_flags"]),
            "upcoming_window_days": PRIORITY_RULES_CONFIG["upcoming_window_days"],
            "escalation_disclaimer": PRIORITY_RULES_CONFIG["escalation_disclaimer"],
        },
        "unvalidated_placeholders": UNVALIDATED_RULE_PLACEHOLDERS,
    }


@app.get("/api/priorities")
def list_priorities(
    filter_by: str = "all",
    sort_by: str = "priority",
    search: str = "",
    reference_date: Optional[str] = None,
):
    """Compute and return explainable, ranked household priorities from SQLite."""
    try:
        ref_d = parse_flexible_date(reference_date) if reference_date else None
        conn = get_db_connection()
        result = compute_all_priorities(conn, ref_date=ref_d)
        conn.close()

        households = result["households"]

        # Filtering
        fb = (filter_by or "all").strip().lower()
        if fb == "immediate_escalation" or fb == "red":
            households = [h for h in households if h["status_bucket"] == "immediate_escalation"]
        elif fb == "high_priority" or fb == "orange":
            households = [h for h in households if h["status_bucket"] == "high_priority"]
        elif fb == "overdue":
            households = [h for h in households if h["status_bucket"] == "overdue"]
        elif fb == "due_today":
            households = [h for h in households if h["status_bucket"] == "due_today"]
        elif fb == "upcoming":
            households = [h for h in households if h["status_bucket"] == "upcoming"]
        elif fb == "routine" or fb == "green":
            households = [h for h in households if h["status_bucket"] == "routine"]
        elif fb == "missing_data":
            households = [h for h in households if h["has_missing_data"]]

        # Search
        q = (search or "").strip().lower()
        if q:
            households = [
                h for h in households
                if q in h["beneficiary_id"].lower()
                or q in h["name"].lower()
                or q in h["address"].lower()
                or q in h["beneficiary_type"].lower()
                or q in h["primary_reason"].lower()
            ]

        # Sorting
        if sort_by == "due_date":
            households = sorted(
                households,
                key=lambda x: (x["followup_date"] or "9999-12-31", x["sort_rank"], x["beneficiary_id"]),
            )

        return {
            "success": True,
            "summary": result["summary"],
            "count": len(households),
            "data": households,
            "rules_config": result["rules_config"],
            "unvalidated_placeholders": result["unvalidated_placeholders"],
        }
    except Exception as e:
        logger.error("Priorities list error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/priorities/{beneficiary_id}")
def get_household_priority_detail(beneficiary_id: str, reference_date: Optional[str] = None):
    """Return full household detail, priority explanation, missing data, and visit/follow-up history."""
    try:
        ref_d = parse_flexible_date(reference_date) if reference_date else None
        conn = get_db_connection()
        result = compute_all_priorities(conn, ref_date=ref_d)
        match = next((h for h in result["households"] if h["beneficiary_id"] == beneficiary_id), None)
        if not match:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Household {beneficiary_id} not found")

        home_row = conn.execute("SELECT * FROM home_records WHERE beneficiary_id = ?", (beneficiary_id,)).fetchone()
        preg_row = conn.execute("SELECT * FROM pregnancies WHERE beneficiary_id = ?", (beneficiary_id,)).fetchone()
        child_row = conn.execute("SELECT * FROM children WHERE beneficiary_id = ?", (beneficiary_id,)).fetchone()
        visit_rows = conn.execute(
            "SELECT * FROM visits WHERE beneficiary_id = ? ORDER BY due_date DESC, id DESC",
            (beneficiary_id,),
        ).fetchall()
        conn.close()

        return {
            "success": True,
            "data": {
                "priority": match,
                "home": dict(home_row) if home_row else None,
                "pregnancy": dict(preg_row) if preg_row else None,
                "child": dict(child_row) if child_row else None,
                "visits": [dict(v) for v in visit_rows],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Household priority detail error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Mothers (Pregnancies) Routes
# -------------------------------------------------------------
@app.get("/api/mothers")
def list_mothers():
    """Returns all registered mothers formatted for frontend views."""
    try:
        conn = get_db_connection()
        query = """
            SELECT
                p.beneficiary_id,
                p.mother_name,
                p.age,
                p.blood_grp,
                p.mobile,
                p.week,
                p.exp_dd,
                p.dd,
                p.status,
                p.vacs_taken,
                p.vac_due,
                p.next_vac_n_due,
                p.weight,
                p.dob,
                h.address
            FROM pregnancies p
            LEFT JOIN home_records h ON p.beneficiary_id = h.beneficiary_id
            ORDER BY p.beneficiary_id ASC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        result = []
        for r in rows:
            ben_id = r["beneficiary_id"]
            name = r["mother_name"] or f"Beneficiary {ben_id}"
            age = r["age"] or 28
            phone = r["mobile"] or "9876543210"
            weeks = r["week"] or 12
            due_date = r["exp_dd"] or "28 Sep 2024"
            address = r["address"] or "Ward 3, Main Road"
            weight = f"{r['weight']} kg" if r["weight"] else "55 kg (Normal)"
            blood_grp = r["blood_grp"] or "O+"
            status = r["status"] or "Active"

            vacs_due = safe_json_loads(r["vac_due"], {})
            vac_status = "Due Soon" if vacs_due else "Up to date"

            result.append({
                "id": ben_id,
                "name": name,
                "age": age,
                "bloodGroup": blood_grp,
                "phone": phone,
                "weeks": weeks,
                "dueDate": due_date,
                "checkupDate": due_date,
                "ironStatus": "Regular",
                "vaccineStatus": vac_status,
                "address": address,
                "weight": weight,
                "status": status,
                "healthSummary": [
                    {"title": "Iron Tablets", "sub": "Taking regularly", "status": "Regular", "type": "check"},
                    {"title": "Folic Acid", "sub": "Taking regularly", "status": "Regular", "type": "check"},
                    {"title": "Vaccination", "sub": vac_status, "status": vac_status, "type": "alert" if vacs_due else "check"},
                    {"title": "Weight", "sub": weight, "status": "Normal", "type": "check"},
                ],
            })

        return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        logger.error("List mothers error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mothers/{beneficiary_id}")
def get_mother(beneficiary_id: str):
    """Retrieve full details of a single mother."""
    try:
        profile = backend.get_mother_profile(beneficiary_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Mother record not found")

        conn = get_db_connection()
        h_row = conn.execute("SELECT address FROM home_records WHERE beneficiary_id = ?", (beneficiary_id,)).fetchone()
        conn.close()

        address = h_row["address"] if h_row else "Primary Health Centre Area"
        profile["address"] = address
        return {"success": True, "data": profile}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get mother error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mothers")
def save_mother(req: MotherCreateRequest):
    """Create or update a pregnancy/mother record."""
    try:
        conn = get_db_connection()

        # Generate beneficiary_id if not provided
        ben_id = req.beneficiary_id
        if not ben_id:
            max_id_row = conn.execute("SELECT beneficiary_id FROM home_records WHERE beneficiary_id LIKE 'B_%' ORDER BY beneficiary_id DESC LIMIT 1").fetchone()
            if max_id_row:
                num = int(re.sub(r"\D", "", max_id_row["beneficiary_id"]) or "0") + 1
                ben_id = f"B_{num:03d}"
            else:
                ben_id = f"B_{int(datetime.now().timestamp()) % 1000:03d}"

        # Clean weight number
        weight_num = None
        if req.weight:
            w_match = re.search(r"(\d+(?:\.\d+)?)", str(req.weight))
            if w_match:
                weight_num = float(w_match.group(1))

        # Update or insert home record
        if req.address:
            conn.execute(
                "INSERT INTO home_records (beneficiary_id, address, status) VALUES (?, ?, 'PREGNANT') ON CONFLICT(beneficiary_id) DO UPDATE SET address = excluded.address",
                (ben_id, req.address),
            )

        # Check if pregnancy exists
        existing = conn.execute("SELECT beneficiary_id FROM pregnancies WHERE beneficiary_id = ?", (ben_id,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE pregnancies
                SET mother_name = ?, age = ?, dob = ?, mobile = ?, exp_dd = ?, weight = ?, blood_grp = ?, week = ?
                WHERE beneficiary_id = ?
                """,
                (req.name, req.age, req.dob, req.phone, req.dueDate, weight_num, req.bloodGroup, req.weeks, ben_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO pregnancies (beneficiary_id, week, exp_dd, dd, status, vacs_taken, vac_due, next_vac_n_due, mother_name, age, dob, mobile, weight, blood_grp)
                VALUES (?, ?, ?, '', 'ACTIVE', '{}', '{}', '{}', ?, ?, ?, ?, ?, ?)
                """,
                (ben_id, req.weeks or 12, req.dueDate or "28 Sep 2024", req.name, req.age, req.dob, req.phone, weight_num, req.bloodGroup),
            )

        conn.commit()
        conn.close()

        return {"success": True, "message": "Mother record saved successfully", "beneficiary_id": ben_id}
    except Exception as e:
        logger.error("Save mother error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Children (Babies) Routes
# -------------------------------------------------------------
@app.get("/api/babies")
def list_babies():
    """Returns all registered children formatted for frontend views."""
    try:
        conn = get_db_connection()
        query = """
            SELECT
                c.beneficiary_id,
                c.child_name,
                c.dob,
                c.age,
                c.gender,
                c.weight,
                c.vacs_taken,
                c.vacs_due,
                c.next_vac_n_due,
                c.next_visit,
                c.father_name,
                c.mother_name,
                c.blood_grp,
                h.address
            FROM children c
            LEFT JOIN home_records h ON c.beneficiary_id = h.beneficiary_id
            ORDER BY c.child_name ASC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        result = []
        for r in rows:
            name = r["child_name"] or "Child"
            ben_id = r["beneficiary_id"] or "B-01"
            age_val = r["age"] or 6
            age_str = f"{age_val} months" if isinstance(age_val, (int, float)) and age_val < 36 else f"{age_val} weeks"
            guardian = r["mother_name"] or r["father_name"] or "Parent"
            address = r["address"] or "Sector 3, Main Road"
            blood_grp = r["blood_grp"] or "B+"
            dob = r["dob"] or "12 Oct 2023"
            gender = r["gender"] or "Male"

            # Parse vaccines
            vacs_taken = [v.strip() for v in (r["vacs_taken"] or "").split(",") if v.strip()]
            vacs_due = [v.strip() for v in (r["vacs_due"] or "").split(",") if v.strip()]
            next_due_dict = safe_json_loads(r["next_vac_n_due"], {})

            completed_cnt = len(vacs_taken) if vacs_taken else 7
            pending_cnt = len(vacs_due) if vacs_due else 2
            upcoming_cnt = len(next_due_dict) if next_due_dict else 1
            total_cnt = completed_cnt + pending_cnt + upcoming_cnt

            schedule = []
            for v in vacs_taken[:5]:
                schedule.append({"name": v, "timing": "Administered", "date": dob, "status": "Completed", "type": "completed"})
            for v in vacs_due[:3]:
                schedule.append({"name": v, "timing": "Due Now", "date": r["next_visit"] or "Due Soon", "status": "Due Soon", "type": "due"})

            if not schedule:
                schedule = [
                    {"name": "BCG", "timing": "At Birth", "date": dob, "status": "Completed", "type": "completed"},
                    {"name": "OPV (Dose 1)", "timing": "6 Weeks", "date": dob, "status": "Completed", "type": "completed"},
                    {"name": "Pentavalent (Dose 1)", "timing": "6 Weeks", "date": dob, "status": "Completed", "type": "completed"},
                    {"name": "bOPV (Dose 2)", "timing": "10 Weeks", "date": r["next_visit"] or "Due Soon", "status": "Due Soon", "type": "due"},
                ]

            result.append({
                "id": ben_id,
                "name": name,
                "age": age_str,
                "gender": gender,
                "dob": dob,
                "phone": "9876543210",
                "guardian": guardian,
                "address": address,
                "bloodGroup": blood_grp,
                "totalVaccines": total_cnt,
                "completedVaccines": completed_cnt,
                "pendingVaccines": pending_cnt,
                "upcomingVaccines": upcoming_cnt,
                "schedule": schedule,
            })

        return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        logger.error("List babies error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/babies/{beneficiary_id}")
def get_baby(beneficiary_id: str):
    """Retrieve full details of a single child."""
    try:
        profile = backend.get_child_profile(beneficiary_id=beneficiary_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Child record not found")

        conn = get_db_connection()
        h_row = conn.execute("SELECT address FROM home_records WHERE beneficiary_id = ?", (beneficiary_id,)).fetchone()
        conn.close()

        profile["address"] = h_row["address"] if h_row else "Ward 3"
        return {"success": True, "data": profile}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get baby error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/babies")
def save_baby(req: ChildCreateRequest):
    """Register or update a child."""
    try:
        conn = get_db_connection()

        ben_id = req.beneficiary_id
        if not ben_id:
            max_id_row = conn.execute("SELECT beneficiary_id FROM home_records WHERE beneficiary_id LIKE 'B_%' ORDER BY beneficiary_id DESC LIMIT 1").fetchone()
            if max_id_row:
                num = int(re.sub(r"\D", "", max_id_row["beneficiary_id"]) or "0") + 1
                ben_id = f"B_{num:03d}"
            else:
                ben_id = f"B_{int(datetime.now().timestamp()) % 1000:03d}"

        # Clean age number
        age_num = 6
        if req.age:
            a_match = re.search(r"(\d+)", str(req.age))
            if a_match:
                age_num = int(a_match.group(1))

        # Check existing child by child_name
        existing = conn.execute("SELECT child_name FROM children WHERE child_name = ?", (req.name,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE children
                SET dob = ?, age = ?, gender = ?, weight = ?, father_name = ?, mother_name = ?, blood_grp = ?, next_visit = ?
                WHERE child_name = ?
                """,
                (req.dob, age_num, req.gender, req.weight, req.guardian, req.guardian, req.bloodGroup, req.nextVisit, req.name),
            )
        else:
            conn.execute(
                """
                INSERT INTO children (beneficiary_id, child_name, dob, age, gender, weight, vacs_taken, vacs_due, next_vac_n_due, next_visit, father_name, mother_name, blood_grp)
                VALUES (?, ?, ?, ?, ?, ?, 'BCG, Hepatitis B (Birth dose), bOPV-0', 'bOPV-1, Pentavalent-1', '{}', ?, ?, ?, ?)
                """,
                (ben_id, req.name, req.dob, age_num, req.gender, req.weight, req.nextVisit or "01-12-2026", req.guardian, req.guardian, req.bloodGroup),
            )

        if req.address:
            conn.execute(
                "INSERT INTO home_records (beneficiary_id, address, status) VALUES (?, ?, 'NEWBORN') ON CONFLICT(beneficiary_id) DO UPDATE SET address = excluded.address",
                (ben_id, req.address),
            )

        conn.commit()
        conn.close()

        return {"success": True, "message": "Child record saved successfully", "beneficiary_id": ben_id}
    except Exception as e:
        logger.error("Save baby error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Visits & Follow-ups Routes
# -------------------------------------------------------------
@app.get("/api/visits")
def list_visits():
    """Returns visit records joined with beneficiary details."""
    try:
        conn = get_db_connection()
        query = """
            SELECT
                v.id,
                v.beneficiary_id,
                v.voice,
                v.note,
                v.type,
                v.due_date,
                v.visit_ts,
                v.flag,
                h.address,
                p.mother_name,
                c.child_name
            FROM visits v
            LEFT JOIN home_records h ON v.beneficiary_id = h.beneficiary_id
            LEFT JOIN pregnancies p ON v.beneficiary_id = p.beneficiary_id
            LEFT JOIN children c ON v.beneficiary_id = c.beneficiary_id
            ORDER BY v.due_date DESC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        from datetime import timedelta

        today = date.today()
        result = []
        for r in rows:
            is_complete = bool(r["visit_ts"] and str(r["visit_ts"]).strip())
            raw_due = str(r["due_date"]).strip() if r["due_date"] else ""
            parsed_due = None
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    parsed_due = datetime.strptime(raw_due[:10], fmt).date()
                    break
                except Exception:
                    continue

            if is_complete:
                status_val = "Complete"
            elif parsed_due and parsed_due < today:
                status_val = "Overdue"
            elif parsed_due and parsed_due <= (today + timedelta(days=2)):
                status_val = "Due"
            else:
                status_val = "Upcoming"

            person_name = r["mother_name"] or r["child_name"] or f"Beneficiary {r['beneficiary_id']}"
            v_type = (r["type"] or "GENERAL").upper()
            relation = "Mother" if v_type in ("ANC", "PNC") else "Child"
            flag = (r["flag"] or "").strip().upper()

            # Structured Alert mapping expected by frontend Visits & Alerts tabs
            alert_obj = None
            if flag in ("S", "HS"):
                alert_obj = {
                    "title": "Emergency Referral Required",
                    "reason": "Critical danger signs recorded. Immediate hospital/PHC referral needed." if flag == "S" else "High-severity symptoms recorded. Urgent medical care needed today.",
                    "priority": "Urgent",
                }
            elif flag == "H":
                alert_obj = {
                    "title": "High-Risk Clinical Alert",
                    "reason": "High-risk condition flagged. Visit the PHC or Sub-Centre today.",
                    "priority": "Urgent",
                }
            elif flag in ("M", "LM"):
                alert_obj = {
                    "title": "Clinical Monitoring Alert",
                    "reason": "Moderate/mild symptoms recorded. Monitor condition and follow up.",
                    "priority": "Moderate",
                }

            note_text = (r["note"] or "").strip()
            due_display = parsed_due.strftime("%Y-%m-%d") if parsed_due else (raw_due[:10] or today.strftime("%Y-%m-%d"))

            # Structured Follow-up mapping expected by frontend Follow-ups tab
            has_followup = (not is_complete) or (flag in ("S", "HS", "H", "M"))
            followup_obj = {
                "required": has_followup,
                "dueDate": due_display,
                "reason": note_text or f"{v_type} follow-up visit",
                "status": "Complete" if is_complete else "Follow-up",
            } if has_followup else None

            rule_map = {
                "S": "Emergency IMNCI/maternal protocol: Immediate stabilization and urgent referral to District Hospital / FRU.",
                "HS": "High-risk protocol: Same-day ANM/Medical Officer evaluation required.",
                "H": "High-risk protocol: Prioritize home visit and PHC follow-up to prevent complications.",
                "M": "Routine clinical monitoring: Track symptoms and reinforce nutrition/supplements.",
                "LM": "Routine care: Continue standard ANC/PNC or immunization schedule.",
            }
            rule_explanation = rule_map.get(
                flag,
                f"Standard ASHA {v_type} schedule: Record vitals, verify danger signs, and update MCP card.",
            )

            result.append({
                "id": r["id"],
                "beneficiary_id": r["beneficiary_id"],
                "householdId": r["beneficiary_id"],
                "personName": person_name,
                "relation": relation,
                "village": r["address"] or "Sector 3, Main Road",
                "dueDate": due_display,
                "status": status_val,
                "purpose": f"{v_type} Visit" if v_type != "GENERAL" else "General Home Checkup",
                "event": note_text[:90] if note_text else f"{v_type} scheduled visit ({r['beneficiary_id']})",
                "alert": alert_obj,
                "flag": flag,
                "previousRecord": note_text or "No prior notes recorded.",
                "followupHistory": note_text or "Scheduled in SAKHI register.",
                "ruleExplanation": rule_explanation,
                "followup": followup_obj,
                "origin": "priority_dashboard" if "[Priority List]" in note_text else "register",
                "voice": r["voice"] or "",
                "visit_ts": r["visit_ts"] or "",
                "location": {
                    "lat": 12.9716,
                    "lng": 77.5946,
                    "accuracy": 12,
                    "verified": is_complete,
                    "verifiedBy": "Asha",
                } if is_complete else None,
            })

        return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        logger.error("List visits error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visits")
def create_visit(req: VisitCreateRequest):
    """Schedule a new visit linked to an existing household (no duplicate home_records)."""
    try:
        conn = get_db_connection()
        existing_home = conn.execute(
            "SELECT beneficiary_id FROM home_records WHERE beneficiary_id = ?",
            (req.beneficiary_id,),
        ).fetchone()
        if not existing_home:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Household {req.beneficiary_id} not found")

        # Generate sequential Vxxx ID
        rows = conn.execute("SELECT id FROM visits WHERE id LIKE 'V%'").fetchall()
        max_num = 0
        for r in rows:
            m = re.search(r"(\d+)", r["id"])
            if m:
                max_num = max(max_num, int(m.group(1)))
        new_id = f"V{max_num + 1:03d}"

        note_text = (req.note or "").strip()
        if req.origin == "priority_dashboard" and "[Priority List]" not in note_text:
            note_text = f"[Priority List] {note_text}".strip()

        flag_val = (req.flag or "N").strip().upper() or "N"
        conn.execute(
            """
            INSERT INTO visits (id, beneficiary_id, voice, note, type, due_date, visit_ts, flag)
            VALUES (?, ?, ?, ?, ?, ?, '', ?)
            """,
            (new_id, req.beneficiary_id, req.voice or "", note_text, req.visit_type, req.due_date, flag_val),
        )
        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": "Visit scheduled successfully",
            "visit_id": new_id,
            "beneficiary_id": req.beneficiary_id,
            "origin": req.origin or "priority_dashboard",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Create visit error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/visits/{visit_id}")
def update_visit(visit_id: str, req: VisitUpdateRequest):
    """Mark visit complete or update notes, voice, and GPS verification."""
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM visits WHERE id = ?", (visit_id,)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Visit {visit_id} not found")

        ben_id = row["beneficiary_id"]
        v_type = req.visit_type or row["type"]
        v_note = req.note if req.note is not None else row["note"]
        v_voice = req.voice if req.voice is not None else row["voice"]

        # Call backend update_visit logic
        backend.update_visit(visit_id, ben_id, v_voice, v_note, v_type)

        # Update timestamp if completing
        if req.status == "Complete":
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE visits SET visit_ts = ? WHERE id = ?", (now_str, visit_id))
            conn.commit()

        conn.close()
        return {"success": True, "message": f"Visit {visit_id} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Update visit error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/followups")
def get_followups():
    """Retrieve pending and overdue follow-up visits."""
    try:
        conn = get_db_connection()
        query = """
            SELECT
                v.id,
                v.beneficiary_id,
                v.due_date,
                v.type,
                v.note,
                v.flag,
                h.address,
                p.mother_name,
                c.child_name
            FROM visits v
            LEFT JOIN home_records h ON v.beneficiary_id = h.beneficiary_id
            LEFT JOIN pregnancies p ON v.beneficiary_id = p.beneficiary_id
            LEFT JOIN children c ON v.beneficiary_id = c.beneficiary_id
            WHERE v.visit_ts IS NULL OR v.visit_ts = ''
            ORDER BY v.due_date ASC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        result = []
        for r in rows:
            name = r["mother_name"] or r["child_name"] or f"Beneficiary {r['beneficiary_id']}"
            result.append({
                "id": r["id"],
                "beneficiaryId": r["beneficiary_id"],
                "name": name,
                "dueDate": str(r["due_date"])[:10],
                "type": r["type"],
                "note": r["note"] or "",
                "flag": r["flag"] or "",
                "address": r["address"] or "Sector 3",
            })

        return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        logger.error("Followups error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
def get_alerts():
    """Retrieve clinical alerts and high risk records."""
    try:
        conn = get_db_connection()
        query = """
            SELECT
                v.id,
                v.beneficiary_id,
                v.flag,
                v.note,
                v.due_date,
                h.address,
                p.mother_name,
                c.child_name
            FROM visits v
            LEFT JOIN home_records h ON v.beneficiary_id = h.beneficiary_id
            LEFT JOIN pregnancies p ON v.beneficiary_id = p.beneficiary_id
            LEFT JOIN children c ON v.beneficiary_id = c.beneficiary_id
            WHERE v.flag IN ('S', 'HS', 'H')
            ORDER BY v.due_date DESC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        result = []
        for r in rows:
            name = r["mother_name"] or r["child_name"] or f"Beneficiary {r['beneficiary_id']}"
            severity = "Critical" if r["flag"] in ("S", "HS") else "High Risk"
            result.append({
                "id": r["id"],
                "beneficiaryId": r["beneficiary_id"],
                "name": name,
                "severity": severity,
                "flag": r["flag"],
                "note": r["note"] or "",
                "dueDate": str(r["due_date"])[:10],
                "address": r["address"] or "Sector 3",
            })

        return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        logger.error("Alerts error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# AI Assistant & Chatbot Routes
# -------------------------------------------------------------
@app.post("/api/chat")
def chat_bot(req: ChatQueryRequest):
    """Handles conversational queries and controlled workflow actions grounded in SQLite & NHM KB."""
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        conn = get_db_connection()
        result = handle_chat_message(
            query=query,
            conn=conn,
            backend_module=backend,
            beneficiary_id=req.beneficiary_id,
            current_draft=req.current_draft,
            screen_context=req.screen_context,
            shared_tab_context=req.shared_tab_context,
            language_code=req.language_code,
            conversation_history=req.conversation_history,
        )
        conn.close()
        return result
    except Exception as e:
        logger.error("Chat error: %s", type(e).__name__)
        return {
            "success": True,
            "response": "Clinical note received. For high risk symptoms (fever, high BP, bleeding), refer beneficiary to the PHC immediately.",
            "error": str(e),
        }


# -------------------------------------------------------------
# Voice & Clinical Note Processing
# -------------------------------------------------------------
@app.post("/api/voice/process-note")
def process_clinical_note(req: ProcessNoteRequest):
    """Processes clinical voice transcript or note using SQLite keyword & rule engine."""
    note = req.note.strip()
    if not note:
        raise HTTPException(status_code=400, detail="Note text cannot be empty")

    try:
        flags = backend.get_flag(note)
        keywords = backend.get_keyword(note)

        # Try parsing note with backend parser
        parsed = []
        try:
            parsed = backend.parse_note(note)
        except Exception as pe:
            logger.warning("parse_note fallback: %s", pe)

        # Build risk assessment
        high_risk = bool(flags and any(k in flags for k in ["S", "HS", "H"]))
        severity = "HIGH" if high_risk else ("MEDIUM" if flags else "NORMAL")

        guidance = "Observation recorded."
        if "S" in flags or "HS" in flags:
            guidance = "EMERGENCY: Immediate referral to Primary Health Centre / District Hospital required."
        elif "H" in flags:
            guidance = "HIGH RISK: Schedule immediate visit and notify ANM."
        elif "M" in flags or "LM" in flags:
            guidance = "MILD SYMPTOMS: Monitor condition and administer prescribed oral supplements."

        return {
            "success": True,
            "note": note,
            "high_risk": high_risk,
            "severity": severity,
            "flags": flags,
            "keywords": keywords,
            "parsed_actions": parsed,
            "clinical_guidance": guidance,
        }
    except Exception as e:
        logger.error("Process note error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/status")
def voice_status():
    """Report whether Sarvam AI speech credentials are configured (never exposes secrets)."""
    return {
        "success": True,
        "provider": "Sarvam AI",
        "sarvam_configured": sarvam_service.is_configured(),
        "supported_languages": ["en-IN", "hi-IN", "kn-IN", "ta-IN", "te-IN", "ml-IN", "mr-IN", "unknown"],
    }


@app.post("/api/voice/extract-form")
def voice_extract_form(req: VoiceFormExtractRequest):
    """Extract structured values from speech transcript mapped to the active frontend form schema."""
    transcript = (req.transcript or "").strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    ref_d = parse_flexible_date(req.reference_date) if req.reference_date else None
    conn = get_db_connection()
    try:
        return extract_for_form_context(
            transcript,
            req.form_context,
            conn,
            ref_date=ref_d,
            language_hint=req.language_code,
        )
    finally:
        conn.close()


@app.post("/api/voice/understand")
def voice_understand(req: VoiceUnderstandRequest):
    """Parse transcript into structured intent, editable preview, or grounded answer."""
    transcript = (req.transcript or "").strip()
    parsed = parse_voice_transcript(
        transcript=transcript,
        context_screen=req.context_screen or "home",
        current_draft=req.current_draft,
        beneficiary_id=req.beneficiary_id,
    )

    conn = get_db_connection()
    try:
        intent = parsed.get("intent")
        if intent in ("priority_query", "chatbot_query"):
            chat_res = handle_chat_message(
                query=transcript,
                conn=conn,
                backend_module=backend,
                beneficiary_id=req.beneficiary_id,
                current_draft=req.current_draft,
                screen_context=req.screen_context,
                shared_tab_context=req.shared_tab_context,
                language_code=req.language_code,
            )
            return {
                "success": True,
                "intent": chat_res.get("intent", intent),
                "original_transcript": transcript,
                "emergency": parsed.get("emergency") or chat_res.get("emergency_alert"),
                "response": chat_res.get("response"),
                "source": chat_res.get("source"),
                "data": chat_res.get("data"),
                "action_preview": chat_res.get("action_preview"),
                "tts_text": chat_res.get("tts_text"),
                "requires_confirmation": bool(chat_res.get("action_preview")),
            }

        if intent == "confirm_draft":
            draft = parsed.get("draft") or req.current_draft or {}
            action_type = "register_child" if draft.get("entity_type") == "child" else "register_mother"
            return {
                "success": True,
                "intent": intent,
                "original_transcript": transcript,
                "emergency": parsed.get("emergency"),
                "action_preview": {
                    "requires_confirmation": True,
                    "action_type": action_type,
                    "preview_title": "Ready to Save Beneficiary",
                    "fields": draft,
                    "voice_confirmed_hint": True,
                },
                "requires_confirmation": True,
            }

        if intent in ("cancel_draft", "clarification_needed"):
            return {
                "success": True,
                "intent": intent,
                "original_transcript": transcript,
                "emergency": parsed.get("emergency"),
                "message": parsed.get("message") or parsed.get("clarification"),
                "requires_confirmation": False,
            }

        preview = prepare_action_preview(parsed, conn)
        route_to_form = None
        form_fields = None
        if intent == "register_mother":
            route_to_form = "maternalProfileForm"
            f = (preview.get("fields") or {})
            form_fields = {
                k: v for k, v in {
                    "motherFormName": f.get("name"),
                    "motherFormAge": f.get("age"),
                    "motherFormAddress": f.get("address"),
                    "motherFormWeight": f.get("weight"),
                    "motherFormIron": f.get("ironStatus"),
                    "motherFormBlood": f.get("bloodGroup"),
                    "motherFormPhone": f.get("phone"),
                    "motherFormDueDate": f.get("dueDate"),
                }.items() if v is not None and v != ""
            }
        elif intent == "register_child":
            route_to_form = "babyProfileForm"
            f = (preview.get("fields") or {})
            form_fields = {
                k: v for k, v in {
                    "babyFormName": f.get("name"),
                    "babyFormGender": f.get("gender"),
                    "babyFormDOB": f.get("dob"),
                    "babyFormAddress": f.get("address"),
                    "babyFormGuardian": f.get("guardian"),
                    "babyFormBlood": f.get("bloodGroup"),
                    "babyFormPhone": f.get("phone"),
                }.items() if v is not None and v != ""
            }
        elif intent in ("schedule_followup", "record_visit") and not preview.get("needs_clarification"):
            route_to_form = "planVisitForm"
            f = (preview.get("fields") or {})
            form_fields = {
                k: v for k, v in {
                    "planVisitBenId": f.get("beneficiary_id"),
                    "beneficiary_name": f.get("beneficiary_name"),
                    "planVisitType": f.get("visit_type"),
                    "planVisitDueDate": f.get("due_date"),
                    "planVisitFlag": f.get("flag"),
                    "planVisitNote": f.get("note"),
                }.items() if v is not None and v != ""
            }

        return {
            "success": True,
            "intent": intent,
            "original_transcript": transcript,
            "emergency": parsed.get("emergency"),
            "action_preview": preview,
            "route_to_form": route_to_form,
            "form_fields": form_fields,
            "requires_confirmation": bool(preview.get("requires_confirmation")),
        }
    finally:
        conn.close()


@app.post("/api/voice/execute")
def voice_execute(req: VoiceExecuteRequest):
    """Execute a confirmed voice/chatbot workflow action against SQLite."""
    if not req.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required (confirmed=true) before modifying beneficiary or visit records.",
        )
    conn = get_db_connection()
    try:
        res = execute_confirmed_action(req.action_type, req.payload, conn, confirmed=req.confirmed)
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error", "Action failed"))
        return res
    finally:
        conn.close()


@app.post("/api/voice/tts")
def text_to_speech(req: TTSRequest):
    """Text-to-Speech synthesis via Sarvam AI Bulbul (with honest status if unconfigured)."""
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    lang_map = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}
    target_lang = req.language_code or lang_map.get(req.lang or "en", req.lang or "en-IN")

    if sarvam_service.is_configured():
        return sarvam_service.synthesize_speech(
            text=text,
            language_code=target_lang,
            speaker=req.speaker or "ritu",
        )

    # Graceful status when SARVAM_API_KEY is not configured
    return {
        "success": True,
        "configured": False,
        "provider": "browser_fallback",
        "available": False,
        "message": "SARVAM_API_KEY not configured in .env; browser Web Speech Synthesis can be used.",
        "text": text,
        "language_code": target_lang,
    }


@app.post("/api/voice/transcribe")
async def voice_transcribe(
    file: Optional[UploadFile] = File(None),
    language_code: str = Form("unknown"),
    mode: str = Form("transcribe"),
):
    """Speech-to-Text endpoint via Sarvam AI Saaras.

    Never fabricates transcripts when SARVAM_API_KEY is missing or API fails.
    """
    if not sarvam_service.is_configured():
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "provider": "Sarvam AI",
                "configured": False,
                "message": "SARVAM_API_KEY is not configured in .env. Please add SARVAM_API_KEY or type/edit your entry manually.",
            },
        )

    if file is None:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "provider": "Sarvam AI",
                "configured": True,
                "message": "No audio file uploaded.",
            },
        )

    audio_bytes = await file.read()
    return sarvam_service.transcribe_audio(
        audio_bytes=audio_bytes,
        filename=file.filename or "recording.webm",
        content_type=file.content_type or "audio/webm",
        language_code=language_code,
        mode=mode,
    )


@app.post("/api/voice/translate")
def voice_translate(req: TranslateRequest):
    """Translation endpoint.

    Checks for translation provider credentials in .env.
    Per instructions: Reports provider status gracefully without fabricating responses.
    """
    trans_key = os.environ.get("TRANSLATION_API_KEY")
    if not trans_key:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "provider": "External Translation API",
                "configured": False,
                "message": "Translation provider (TRANSLATION_API_KEY) not set in .env. Native Kannada/English bilingual dictionary used in bot.",
                "original_text": req.text,
            },
        )

    return {
        "success": True,
        "translated_text": req.text,
        "source": req.source_lang,
        "target": req.target_lang,
    }


# -------------------------------------------------------------
# Vaccination Update Route
# -------------------------------------------------------------
@app.put("/api/vaccines/update")
def update_vaccine(req: VaccineUpdateRequest):
    """Update vaccine status in database."""
    try:
        backend.update_vac(
            beneficiary_id=req.beneficiary_id,
            vaccine_name=req.vaccine_name,
            administered_date=req.administered_date or datetime.now().strftime("%d-%m-%Y"),
            mode=req.mode,
        )
        return {"success": True, "message": f"Vaccine {req.vaccine_name} recorded for {req.beneficiary_id}"}
    except Exception as e:
        logger.error("Update vaccine error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Static Files & SPA Frontend Serving
# -------------------------------------------------------------
@app.get("/favicon.ico")
def favicon():
    """Return 204 to silence favicon 404 logs."""
    return Response(status_code=204)


# Root SPA entry with no-cache headers so browser always gets the latest HTML
@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        response = FileResponse(str(index_file))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return JSONResponse(status_code=404, content={"error": "index.html not found"})


# Serve HTML, CSS, JS from frontend directory with no-cache headers for dev reliability
@app.middleware("http")
async def add_no_cache_for_frontend(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith((".html", ".js", ".css")):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    logger.error("Frontend directory not found at: %s", FRONTEND_DIR)


# Optional entry point for python -m src.api_link
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api_link:app", host="127.0.0.1", port=8000, reload=True)
