"""SAKHI — Voice Action Preview, Validation & Controlled Execution Service.

Prepares editable previews for consequential workflow actions (beneficiary
registration, visit recording, follow-up creation/completion/reschedule)
and executes database writes ONLY when `confirmed=True`.
"""

from datetime import date, datetime
import re
import sqlite3
from typing import Any, Dict, List, Optional


def _find_beneficiary(conn: sqlite3.Connection, name: Optional[str], ben_id: Optional[str]) -> List[Dict[str, Any]]:
    if ben_id:
        row = conn.execute(
            """
            SELECT h.beneficiary_id, h.address, h.status,
                   COALESCE(p.mother_name, c.child_name, h.beneficiary_id) AS display_name
            FROM home_records h
            LEFT JOIN pregnancies p ON h.beneficiary_id = p.beneficiary_id
            LEFT JOIN children c ON h.beneficiary_id = c.beneficiary_id
            WHERE h.beneficiary_id = ?
            """,
            (ben_id,),
        ).fetchone()
        if row:
            return [dict(row)]

    if not name:
        return []

    q = f"%{name.strip().lower()}%"
    rows = conn.execute(
        """
        SELECT h.beneficiary_id, h.address, h.status,
               COALESCE(p.mother_name, c.child_name, h.beneficiary_id) AS display_name
        FROM home_records h
        LEFT JOIN pregnancies p ON h.beneficiary_id = p.beneficiary_id
        LEFT JOIN children c ON h.beneficiary_id = c.beneficiary_id
        WHERE LOWER(COALESCE(p.mother_name, '')) LIKE ?
           OR LOWER(COALESCE(c.child_name, '')) LIKE ?
           OR LOWER(h.beneficiary_id) LIKE ?
        """,
        (q, q, q),
    ).fetchall()
    return [dict(r) for r in rows]


def _check_duplicate_beneficiary(conn: sqlite3.Connection, name: Optional[str], phone: Optional[str], entity_type: str) -> List[Dict[str, Any]]:
    if not name and not phone:
        return []
    matches = []
    if entity_type == "child" and name:
        rows = conn.execute(
            "SELECT beneficiary_id, child_name AS name FROM children WHERE LOWER(child_name) = LOWER(?)",
            (name.strip(),),
        ).fetchall()
        matches.extend([dict(r) for r in rows])
    elif entity_type == "mother":
        if name:
            rows = conn.execute(
                "SELECT beneficiary_id, mother_name AS name, mobile FROM pregnancies WHERE LOWER(mother_name) = LOWER(?)",
                (name.strip(),),
            ).fetchall()
            matches.extend([dict(r) for r in rows])
        if phone:
            rows = conn.execute(
                "SELECT beneficiary_id, mother_name AS name, mobile FROM pregnancies WHERE mobile = ?",
                (phone.strip(),),
            ).fetchall()
            for r in rows:
                if not any(m["beneficiary_id"] == r["beneficiary_id"] for m in matches):
                    matches.append(dict(r))
    return matches


def prepare_action_preview(parsed: Dict[str, Any], conn: sqlite3.Connection) -> Dict[str, Any]:
    """Validate extracted entities, detect duplicates/missing fields, and build editable preview."""
    intent = parsed.get("intent")

    if intent in ("register_mother", "register_child"):
        fields = dict(parsed.get("fields") or {})
        entity_type = fields.get("entity_type", "mother")
        missing: List[str] = []
        if not fields.get("name"):
            missing.append("Full Name")
        if not fields.get("address"):
            missing.append("Address / Ward")
        if entity_type == "mother" and not fields.get("weeks") and not fields.get("dueDate"):
            missing.append("Pregnancy Weeks or Due Date")
        if entity_type == "child" and not fields.get("age"):
            missing.append("Child Age or DOB")

        duplicates = _check_duplicate_beneficiary(conn, fields.get("name"), fields.get("phone"), entity_type)
        return {
            "requires_confirmation": True,
            "action_type": intent,
            "preview_title": "Confirm New Mother Registration" if entity_type == "mother" else "Confirm New Child Registration",
            "fields": fields,
            "missing_fields": missing,
            "potential_duplicates": duplicates,
            "clarification": (
                f"Potential duplicate found for {fields.get('name')}: {', '.join(d['beneficiary_id'] for d in duplicates)}. Please verify before saving."
                if duplicates else (
                    f"Please review and fill missing field(s): {', '.join(missing)} before confirming."
                    if missing else None
                )
            ),
        }

    if intent == "correct_draft":
        draft = parsed.get("draft") or {}
        return {
            "requires_confirmation": True,
            "action_type": "register_child" if draft.get("entity_type") == "child" else "register_mother",
            "preview_title": "Updated Registration Preview",
            "fields": draft,
            "changes": parsed.get("changes") or [],
            "missing_fields": [],
            "potential_duplicates": [],
        }

    if intent in ("record_visit", "schedule_followup", "complete_followup", "reschedule_followup", "cancel_followup"):
        if parsed.get("date_ambiguous"):
            return {
                "requires_confirmation": False,
                "needs_clarification": True,
                "clarification": parsed.get("clarification"),
            }

        matches = _find_beneficiary(conn, parsed.get("target_name"), parsed.get("beneficiary_id"))
        if not matches:
            return {
                "requires_confirmation": False,
                "needs_clarification": True,
                "clarification": (
                    f"Could not reliably identify household/beneficiary '{parsed.get('target_name') or ''}'. "
                    "Please select or specify the beneficiary ID (e.g. B_001) or full name."
                ),
            }
        if len(matches) > 1 and not parsed.get("beneficiary_id"):
            return {
                "requires_confirmation": False,
                "needs_clarification": True,
                "candidate_beneficiaries": matches,
                "clarification": "Multiple matching beneficiaries found. Please confirm which household you mean: "
                + ", ".join(f"{m['display_name']} ({m['beneficiary_id']})" for m in matches),
            }

        ben = matches[0]
        ben_id = ben["beneficiary_id"]
        pending_visits = [
            dict(r) for r in conn.execute(
                "SELECT id, type, due_date, flag, note FROM visits WHERE beneficiary_id = ? AND (visit_ts IS NULL OR visit_ts = '') ORDER BY due_date ASC",
                (ben_id,),
            ).fetchall()
        ]

        if intent == "cancel_followup" and not pending_visits:
            return {
                "requires_confirmation": False,
                "needs_clarification": True,
                "clarification": f"No pending follow-up found for {ben['display_name']} ({ben_id}).",
            }

        fields = {
            "beneficiary_id": ben_id,
            "beneficiary_name": ben["display_name"],
            "address": ben["address"],
            "visit_id": pending_visits[0]["id"] if pending_visits else None,
            "visit_type": parsed.get("visit_type") or (pending_visits[0]["type"] if pending_visits else "GENERAL"),
            "due_date": parsed.get("due_date") or (pending_visits[0]["due_date"] if pending_visits else date.today().isoformat()),
            "followup_requested": parsed.get("followup_requested", False),
            "followup_date": parsed.get("followup_date"),
            "flag": parsed.get("flag") or "N",
            "note": parsed.get("note") or "",
        }
        title_map = {
            "record_visit": f"Confirm Visit Record · {ben['display_name']} ({ben_id})",
            "schedule_followup": f"Confirm Follow-up Schedule · {ben['display_name']} ({ben_id})",
            "complete_followup": f"Confirm Completion · {ben['display_name']} ({ben_id})",
            "reschedule_followup": f"Confirm Reschedule · {ben['display_name']} ({ben_id})",
            "cancel_followup": f"Confirm Cancellation · {ben['display_name']} ({ben_id})",
        }
        return {
            "requires_confirmation": True,
            "action_type": intent,
            "preview_title": title_map.get(intent, "Confirm Action"),
            "fields": fields,
            "pending_visits": pending_visits,
        }

    return {"requires_confirmation": False, "action_type": intent}


def execute_confirmed_action(
    action_type: str,
    payload: Dict[str, Any],
    conn: sqlite3.Connection,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Execute a validated workflow action ONLY when confirmed=True."""
    if not confirmed:
        return {
            "success": False,
            "error": "Explicit user confirmation is required before saving or modifying records.",
        }

    if action_type == "register_mother":
        name = (payload.get("name") or "").strip()
        if not name:
            return {"success": False, "error": "Mother name is required."}

        max_row = conn.execute(
            "SELECT beneficiary_id FROM home_records WHERE beneficiary_id LIKE 'B_%' ORDER BY beneficiary_id DESC LIMIT 1"
        ).fetchone()
        num = int(re.sub(r"\D", "", max_row["beneficiary_id"]) or "0") + 1 if max_row else 1
        ben_id = payload.get("beneficiary_id") or f"B_{num:03d}"

        weight_num = None
        if payload.get("weight") is not None:
            m = re.search(r"(\d+(?:\.\d+)?)", str(payload["weight"]))
            if m:
                weight_num = float(m.group(1))

        conn.execute(
            "INSERT INTO home_records (beneficiary_id, address, status) VALUES (?, ?, 'PREGNANT') "
            "ON CONFLICT(beneficiary_id) DO UPDATE SET address = excluded.address",
            (ben_id, payload.get("address") or ""),
        )
        conn.execute(
            """
            INSERT INTO pregnancies (beneficiary_id, week, exp_dd, dd, status, vacs_taken, vac_due, next_vac_n_due, mother_name, age, dob, mobile, weight, blood_grp)
            VALUES (?, ?, ?, '', 'ACTIVE', '{}', NULL, '{}', ?, ?, ?, ?, ?, ?)
            """,
            (
                ben_id,
                payload.get("weeks"),
                payload.get("dueDate") or "",
                name,
                payload.get("age"),
                payload.get("dob") or "",
                payload.get("phone") or "",
                weight_num,
                payload.get("bloodGroup") or "",
            ),
        )
        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "beneficiary_id": ben_id,
            "message": f"Beneficiary {name} ({ben_id}) registered successfully.",
        }

    if action_type == "register_child":
        name = (payload.get("name") or "").strip()
        if not name:
            return {"success": False, "error": "Child name is required."}

        max_row = conn.execute(
            "SELECT beneficiary_id FROM home_records WHERE beneficiary_id LIKE 'B_%' ORDER BY beneficiary_id DESC LIMIT 1"
        ).fetchone()
        num = int(re.sub(r"\D", "", max_row["beneficiary_id"]) or "0") + 1 if max_row else 1
        ben_id = payload.get("beneficiary_id") or f"B_{num:03d}"

        age_num = None
        if payload.get("age"):
            m = re.search(r"(\d+)", str(payload["age"]))
            if m:
                age_num = int(m.group(1))

        weight_num = None
        if payload.get("weight") is not None:
            m = re.search(r"(\d+(?:\.\d+)?)", str(payload["weight"]))
            if m:
                weight_num = float(m.group(1))

        vacs_due = "Pending verification" if payload.get("vaccinationStatus") == "Incomplete" else ""

        conn.execute(
            "INSERT INTO home_records (beneficiary_id, address, status) VALUES (?, ?, 'INFANT') "
            "ON CONFLICT(beneficiary_id) DO UPDATE SET address = excluded.address",
            (ben_id, payload.get("address") or ""),
        )
        conn.execute(
            """
            INSERT INTO children (beneficiary_id, child_name, dob, age, gender, weight, vacs_taken, vacs_due, next_vac_n_due, next_visit, father_name, mother_name, blood_grp)
            VALUES (?, ?, ?, ?, ?, ?, '', ?, '{}', ?, ?, ?, ?)
            """,
            (
                ben_id,
                name,
                payload.get("dob") or "",
                age_num,
                payload.get("gender") or "",
                weight_num,
                vacs_due,
                payload.get("nextVisit") or "",
                payload.get("guardian") or "",
                payload.get("guardian") or "",
                payload.get("bloodGroup") or "",
            ),
        )
        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "beneficiary_id": ben_id,
            "message": f"Child {name} ({ben_id}) registered successfully.",
        }

    if action_type == "record_visit":
        ben_id = payload.get("beneficiary_id")
        if not ben_id:
            return {"success": False, "error": "Beneficiary ID is required."}
        existing_home = conn.execute("SELECT beneficiary_id FROM home_records WHERE beneficiary_id = ?", (ben_id,)).fetchone()
        if not existing_home:
            return {"success": False, "error": f"Household {ben_id} not found."}

        rows = conn.execute("SELECT id FROM visits WHERE id LIKE 'V%'").fetchall()
        max_num = max([int(re.search(r"(\d+)", r["id"]).group(1)) for r in rows if re.search(r"(\d+)", r["id"])], default=0)

        vid = f"V{max_num + 1:03d}"
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO visits (id, beneficiary_id, voice, note, type, due_date, visit_ts, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                vid,
                ben_id,
                payload.get("note") or "",
                f"[Voice Visit] {payload.get('note') or ''}".strip(),
                payload.get("visit_type") or "GENERAL",
                payload.get("due_date") or date.today().isoformat(),
                now_ts,
                (payload.get("flag") or "N").upper(),
            ),
        )

        followup_id = None
        if payload.get("followup_requested") and payload.get("followup_date"):
            followup_id = f"V{max_num + 2:03d}"
            conn.execute(
                "INSERT INTO visits (id, beneficiary_id, voice, note, type, due_date, visit_ts, flag) VALUES (?, ?, '', ?, ?, ?, '', 'N')",
                (
                    followup_id,
                    ben_id,
                    f"[Priority List] Follow-up scheduled after {vid}",
                    payload.get("visit_type") or "GENERAL",
                    payload["followup_date"],
                ),
            )

        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "visit_id": vid,
            "followup_id": followup_id,
            "beneficiary_id": ben_id,
            "message": f"Visit {vid} recorded for {ben_id}" + (f" and follow-up {followup_id} scheduled." if followup_id else "."),
        }

    if action_type == "schedule_followup":
        ben_id = payload.get("beneficiary_id")
        due_date = payload.get("due_date")
        if not ben_id or not due_date:
            return {"success": False, "error": "Beneficiary ID and due date are required."}
        rows = conn.execute("SELECT id FROM visits WHERE id LIKE 'V%'").fetchall()
        max_num = max([int(re.search(r"(\d+)", r["id"]).group(1)) for r in rows if re.search(r"(\d+)", r["id"])], default=0)
        vid = f"V{max_num + 1:03d}"
        conn.execute(
            "INSERT INTO visits (id, beneficiary_id, voice, note, type, due_date, visit_ts, flag) VALUES (?, ?, '', ?, ?, ?, '', ?)",
            (
                vid,
                ben_id,
                f"[Priority List] {payload.get('note') or 'Scheduled follow-up'}".strip(),
                payload.get("visit_type") or "GENERAL",
                due_date,
                (payload.get("flag") or "N").upper(),
            ),
        )
        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "visit_id": vid,
            "beneficiary_id": ben_id,
            "message": f"Follow-up {vid} scheduled for {ben_id} on {due_date}.",
        }

    if action_type == "complete_followup":
        vid = payload.get("visit_id")
        ben_id = payload.get("beneficiary_id")
        if not vid and ben_id:
            row = conn.execute(
                "SELECT id FROM visits WHERE beneficiary_id = ? AND (visit_ts IS NULL OR visit_ts = '') ORDER BY due_date ASC LIMIT 1",
                (ben_id,),
            ).fetchone()
            vid = row["id"] if row else None
        if not vid:
            return {"success": False, "error": "No pending visit or follow-up found to complete."}
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE visits SET visit_ts = ? WHERE id = ?", (now_ts, vid))
        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "visit_id": vid,
            "message": f"Follow-up/visit {vid} marked complete.",
        }

    if action_type == "reschedule_followup":
        vid = payload.get("visit_id")
        due_date = payload.get("due_date")
        if not vid or not due_date:
            return {"success": False, "error": "Visit ID and new due date are required."}
        conn.execute("UPDATE visits SET due_date = ? WHERE id = ?", (due_date, vid))
        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "visit_id": vid,
            "message": f"Visit {vid} rescheduled to {due_date}.",
        }

    if action_type == "cancel_followup":
        vid = payload.get("visit_id")
        if not vid:
            return {"success": False, "error": "Visit ID is required to cancel a follow-up."}
        conn.execute("DELETE FROM visits WHERE id = ? AND (visit_ts IS NULL OR visit_ts = '')", (vid,))
        conn.commit()
        return {
            "success": True,
            "action_type": action_type,
            "visit_id": vid,
            "message": f"Pending follow-up {vid} cancelled.",
        }

    return {"success": False, "error": f"Unsupported action type: {action_type}"}
