"""SAKHI — Transparent Rule-Based Household Prioritization Engine.

Deterministic, explainable, and configurable workflow prioritization for ASHA workers.
Does NOT use LLMs for risk scoring and does NOT invent clinical thresholds.
Missing data is explicitly flagged for verification and is never treated as low risk.
"""

from datetime import date, datetime, timedelta
import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Configurable Rule Definitions & Explicit Clinical Placeholders
# ---------------------------------------------------------------------------
PRIORITY_LEVELS = {
    "RED": {
        "code": "RED",
        "label": "Immediate Escalation",
        "rank": 0,
        "description": "Triggered only by explicitly configured danger-sign / emergency indicators.",
    },
    "ORANGE": {
        "code": "ORANGE",
        "label": "High Priority",
        "rank": 1,
        "description": "Validated high-priority follow-up situations per configured rules.",
    },
    "YELLOW": {
        "code": "YELLOW",
        "label": "Due / Overdue",
        "rank": 2,
        "description": "Follow-up or vaccination activities that are overdue or due today.",
    },
    "GREEN": {
        "code": "GREEN",
        "label": "Routine",
        "rank": 4,
        "description": "No currently flagged urgent, high-priority, or due/overdue activity.",
    },
}

# Explicitly configured flags matching SQLite `keyword4` table
PRIORITY_RULES_CONFIG = {
    "emergency_flags": {"S", "HS"},
    "high_priority_flags": {"H", "HM"},
    "moderate_flags": {"M", "LM"},
    "upcoming_window_days": 7,
    "escalation_disclaimer": (
        "Workflow escalation alert only — SAKHI does not diagnose medical emergencies. "
        "Do not wait for a scheduled visit; follow PHC/ANM escalation protocol."
    ),
}

# Rules explicitly marked as placeholders awaiting clinical validation
UNVALIDATED_RULE_PLACEHOLDERS = [
    {
        "id": "PLACEHOLDER_VITALS_THRESHOLDS",
        "area": "Maternal Vitals (BP, Hemoglobin, Weight Gain)",
        "status": "Placeholder — Awaiting Clinical Validation",
        "note": "Numeric BP/Hb/weight cutoffs are NOT auto-scored; only recorded high-risk status or worker-entered flags are used.",
    },
    {
        "id": "PLACEHOLDER_PNC_DAY_WINDOWS",
        "area": "Postnatal Day-Count Intervals (Day 1, 3, 7, 14, 21, 28)",
        "status": "Placeholder — Awaiting Clinical Validation",
        "note": "Delivery-date-to-PNC day-window auto-generation awaits formal state NHM sign-off; currently relies on scheduled visit due dates.",
    },
    {
        "id": "PLACEHOLDER_SYMPTOM_NLP_AUTO_ESCALATION",
        "area": "Free-Text Voice Note Auto-Escalation",
        "status": "Placeholder — Human Confirmation Required",
        "note": "Keyword detection assists review only; emergency escalation requires explicit recorded flag (S/HS) or worker confirmation.",
    },
]


def parse_flexible_date(val: Any) -> Optional[date]:
    """Parse YYYY-MM-DD, DD-MM-YYYY, or DD/MM/YYYY into a date object."""
    if not val:
        return None
    s = str(val).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _safe_json_dict(val: Any) -> Dict[str, Any]:
    if not val:
        return {}
    if isinstance(val, dict):
        return val
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _load_flag_messages(conn: sqlite3.Connection) -> Dict[str, str]:
    """Load configured flag messages from keyword4 table."""
    defaults = {
        "S": "Emergency! Go to hospital NOW.",
        "HS": "Urgent medical care needed today.",
        "H": "Visit the PHC or Sub-Centre today.",
        "HM": "Symptoms are worsening. See ANM/Doctor by tomorrow.",
        "M": "Provide basic supportive care at home as appropriate.",
        "LM": "Follow general comfort and self-care practices at home.",
        "L": "No immediate illness, but needs prevention.",
        "N": "Everything looks healthy and normal.",
    }
    try:
        rows = conn.execute("SELECT flag, msg FROM keyword4").fetchall()
        for r in rows:
            f = (r["flag"] or "").strip().upper()
            m = (r["msg"] or "").strip()
            if f and m:
                defaults[f] = m
    except Exception:
        pass
    return defaults


def _detect_missing_data(
    home: Dict[str, Any],
    preg: Optional[Dict[str, Any]],
    child: Optional[Dict[str, Any]],
) -> List[str]:
    """Identify missing or incomplete fields that require ASHA verification."""
    missing: List[str] = []
    if not (home.get("address") or "").strip():
        missing.append("Household address")

    if preg:
        if not (preg.get("mother_name") or "").strip():
            missing.append("Mother name")
        if not (preg.get("mobile") or "").strip():
            missing.append("Mother mobile number")
        if preg.get("weight") is None:
            missing.append("Maternal weight")
        if not (preg.get("exp_dd") or "").strip():
            missing.append("Expected delivery date")
        if (preg.get("status") or "").upper() == "ACTIVE" and preg.get("vac_due") is None:
            missing.append("Pregnancy vaccination schedule")

    if child:
        if not (child.get("child_name") or "").strip():
            missing.append("Child name")
        if not (child.get("dob") or "").strip():
            missing.append("Child date of birth")
        if child.get("weight") is None:
            missing.append("Child weight")
        if not (child.get("next_visit") or "").strip():
            missing.append("Child next visit date")

    return missing


def evaluate_household_priority(
    home: Dict[str, Any],
    preg: Optional[Dict[str, Any]],
    child: Optional[Dict[str, Any]],
    visits: List[Dict[str, Any]],
    flag_messages: Dict[str, str],
    ref_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Evaluate a single household using deterministic, explainable rules."""
    today = ref_date or date.today()
    ben_id = home["beneficiary_id"]
    address = (home.get("address") or "").strip() or "Address missing — verify"
    home_status = (home.get("status") or "GENERAL").strip().upper()

    # Determine beneficiary display name & type
    mother_name = (preg.get("mother_name") or "").strip() if preg else ""
    child_name = (child.get("child_name") or "").strip() if child else ""
    if mother_name and child_name:
        display_name = f"{mother_name} & {child_name}"
    elif mother_name:
        display_name = mother_name
    elif child_name:
        display_name = f"{child_name} (Child)"
    else:
        display_name = f"Household {ben_id}"

    type_map = {
        "PREGNANT": "Pregnant Mother",
        "NEWBORN": "Newborn",
        "INFANT": "Infant / Child",
        "POSTDELIVERY": "Postnatal Mother",
    }
    beneficiary_type = type_map.get(home_status, home_status.title() if home_status else "Household")
    if preg and child:
        beneficiary_type = "Mother & Child"

    # Sort visits chronologically (most recent due_date first)
    def visit_sort_key(v: Dict[str, Any]) -> Tuple[date, str]:
        d = parse_flexible_date(v.get("due_date")) or date(1900, 1, 1)
        return (d, str(v.get("id") or ""))

    sorted_visits = sorted(visits, key=visit_sort_key, reverse=True)
    pending_visits = [v for v in sorted_visits if not (v.get("visit_ts") and str(v.get("visit_ts")).strip())]
    completed_visits = [v for v in sorted_visits if v.get("visit_ts") and str(v.get("visit_ts")).strip()]

    # Collect signals & explanations
    reasons: List[str] = []
    triggered_rules: List[Dict[str, Any]] = []
    escalation_info: Optional[Dict[str, Any]] = None

    # 1. Check RED — Immediate Escalation (explicitly configured S / HS flags on pending/unclosed visits)
    emergency_pending = [
        v for v in pending_visits
        if (v.get("flag") or "").strip().upper() in PRIORITY_RULES_CONFIG["emergency_flags"]
    ]
    # Also check if the most recent visit overall is an emergency flag with no subsequent normal visit
    latest_visit = sorted_visits[0] if sorted_visits else None
    latest_flag = (latest_visit.get("flag") or "").strip().upper() if latest_visit else ""

    is_red = False
    if emergency_pending:
        is_red = True
        ev = emergency_pending[0]
        eflag = (ev.get("flag") or "").strip().upper()
        emsg = flag_messages.get(eflag, "Urgent medical care needed today.")
        reason_txt = f"Recorded urgent indicator (Flag {eflag}) on visit {ev['id']}: {emsg}"
        reasons.append(reason_txt)
        triggered_rules.append({"rule": "RED_EMERGENCY_FLAG", "visit_id": ev["id"], "flag": eflag, "detail": reason_txt})
        escalation_info = {
            "warning": "IMMEDIATE ESCALATION REQUIRED",
            "trigger_indicator": f"Recorded Flag '{eflag}' on Visit {ev['id']}" + (f" ({ev['note']})" if ev.get("note") else ""),
            "instruction": emsg,
            "disclaimer": PRIORITY_RULES_CONFIG["escalation_disclaimer"],
        }

    # 2. Check ORANGE — High Priority
    is_orange = False
    high_pending = [
        v for v in pending_visits
        if (v.get("flag") or "").strip().upper() in PRIORITY_RULES_CONFIG["high_priority_flags"]
    ]
    if high_pending:
        is_orange = True
        hv = high_pending[0]
        hflag = (hv.get("flag") or "").strip().upper()
        hmsg = flag_messages.get(hflag, "High-priority follow-up required.")
        reason_txt = f"Recorded high-priority flag ({hflag}) on pending visit {hv['id']}: {hmsg}"
        reasons.append(reason_txt)
        triggered_rules.append({"rule": "ORANGE_HIGH_FLAG", "visit_id": hv["id"], "flag": hflag, "detail": reason_txt})

    if preg and (preg.get("status") or "").strip().upper() == "HIGH_RISK":
        is_orange = True
        reason_txt = "Pregnancy record is marked HIGH_RISK and requires priority follow-up."
        reasons.append(reason_txt)
        triggered_rules.append({"rule": "ORANGE_HIGH_RISK_PREGNANCY", "detail": reason_txt})

    if not is_red and latest_visit and latest_flag in PRIORITY_RULES_CONFIG["emergency_flags"] and latest_visit in completed_visits:
        is_orange = True
        reason_txt = (
            f"Previously recorded emergency flag ({latest_flag}) on visit {latest_visit['id']} "
            "requires post-escalation follow-up verification."
        )
        reasons.append(reason_txt)
        triggered_rules.append({"rule": "ORANGE_POST_ESCALATION_FOLLOWUP", "visit_id": latest_visit["id"], "detail": reason_txt})

    # 3. Check Follow-up Due / Overdue / Upcoming (Pending visits + Child vaccination schedule)
    overdue_days = 0
    due_today_flag = False
    upcoming_flag = False
    next_followup_date: Optional[date] = None

    for pv in pending_visits:
        d = parse_flexible_date(pv.get("due_date"))
        if d:
            if next_followup_date is None or d < next_followup_date:
                next_followup_date = d
            delta = (today - d).days
            if delta > 0:
                overdue_days = max(overdue_days, delta)
                reason_txt = f"Follow-up ({pv.get('type') or 'Visit'}) overdue by {delta} day{'s' if delta != 1 else ''} (due {d.isoformat()})."
                reasons.append(reason_txt)
                triggered_rules.append({"rule": "YELLOW_OVERDUE_VISIT", "visit_id": pv["id"], "days": delta, "detail": reason_txt})
            elif delta == 0:
                due_today_flag = True
                reason_txt = f"Scheduled follow-up ({pv.get('type') or 'Visit'}) is due today ({d.isoformat()})."
                reasons.append(reason_txt)
                triggered_rules.append({"rule": "YELLOW_DUE_TODAY", "visit_id": pv["id"], "detail": reason_txt})
            elif (d - today).days <= PRIORITY_RULES_CONFIG["upcoming_window_days"]:
                upcoming_flag = True
                reason_txt = f"Upcoming follow-up ({pv.get('type') or 'Visit'}) scheduled on {d.isoformat()}."
                reasons.append(reason_txt)
                triggered_rules.append({"rule": "UPCOMING_VISIT", "visit_id": pv["id"], "detail": reason_txt})
            else:
                upcoming_flag = True

    # Check child vaccination schedule
    if child:
        raw_vacs_due = (child.get("vacs_due") or "").strip()
        if raw_vacs_due.startswith("{"):
            parsed_vacs = _safe_json_dict(raw_vacs_due)
            vacs_due_str = ", ".join(parsed_vacs.keys()) if parsed_vacs else ""
        else:
            vacs_due_str = raw_vacs_due
        child_next = parse_flexible_date(child.get("next_visit"))
        if child_next:
            if next_followup_date is None or child_next < next_followup_date:
                next_followup_date = child_next
            cdelta = (today - child_next).days
            if cdelta > 0 and vacs_due_str:
                overdue_days = max(overdue_days, cdelta)
                reason_txt = f"Vaccination schedule ({vacs_due_str}) overdue by {cdelta} day{'s' if cdelta != 1 else ''}."
                reasons.append(reason_txt)
                triggered_rules.append({"rule": "YELLOW_VACCINE_OVERDUE", "days": cdelta, "detail": reason_txt})
            elif cdelta == 0 and vacs_due_str:
                due_today_flag = True
                reason_txt = f"Vaccination schedule indicates due activity today ({vacs_due_str})."
                reasons.append(reason_txt)
                triggered_rules.append({"rule": "YELLOW_VACCINE_DUE_TODAY", "detail": reason_txt})
            elif (child_next - today).days <= PRIORITY_RULES_CONFIG["upcoming_window_days"] and vacs_due_str:
                upcoming_flag = True
                reason_txt = f"Upcoming vaccination due on {child_next.isoformat()} ({vacs_due_str})."
                reasons.append(reason_txt)
                triggered_rules.append({"rule": "UPCOMING_VACCINE", "detail": reason_txt})

    # 4. Missing / Incomplete Data Detection (never treated as safe/low-risk)
    missing_items = _detect_missing_data(home, preg, child)
    has_missing_data = len(missing_items) > 0
    if has_missing_data:
        missing_summary = ", ".join(missing_items[:3]) + (f" (+{len(missing_items) - 3} more)" if len(missing_items) > 3 else "")
        verification_warning = f"Missing information requires verification: {missing_summary}."
    else:
        verification_warning = None

    # 5. Determine Final Priority Category (RED cannot be downgraded!)
    if is_red:
        priority_code = "RED"
        priority_label = "Immediate Escalation"
        status_bucket = "immediate_escalation"
        sort_rank = 0
        suggested_action = "Escalate immediately to PHC / Medical Officer — do not wait for scheduled visit."
    elif is_orange:
        priority_code = "ORANGE"
        priority_label = "High Priority"
        status_bucket = "high_priority"
        sort_rank = 1
        suggested_action = "Plan priority home visit / ANM coordination today."
    elif overdue_days > 0:
        priority_code = "YELLOW"
        priority_label = "Overdue"
        status_bucket = "overdue"
        sort_rank = 2
        suggested_action = "Conduct overdue follow-up visit immediately and update record."
    elif due_today_flag:
        priority_code = "YELLOW"
        priority_label = "Due Today"
        status_bucket = "due_today"
        sort_rank = 3
        suggested_action = "Complete scheduled visit or vaccination activity today."
    elif upcoming_flag:
        priority_code = "GREEN"
        priority_label = "Upcoming"
        status_bucket = "upcoming"
        sort_rank = 4
        suggested_action = "Prepare for upcoming scheduled follow-up."
    else:
        priority_code = "GREEN"
        priority_label = "Routine"
        status_bucket = "routine"
        sort_rank = 5
        suggested_action = (
            "Verify missing household details during next routine round."
            if has_missing_data
            else "No pending action; maintain routine household schedule."
        )

    if not reasons:
        if has_missing_data:
            reasons.append("No scheduled follow-up flagged, but missing record details require verification.")
        else:
            reasons.append("No active danger signs, high-risk flags, or overdue follow-ups.")

    primary_reason = reasons[0]
    next_date_str = next_followup_date.isoformat() if next_followup_date else (
        parse_flexible_date(preg.get("exp_dd")).isoformat() if preg and parse_flexible_date(preg.get("exp_dd")) else None
    )

    return {
        "beneficiary_id": ben_id,
        "name": display_name,
        "address": address,
        "beneficiary_type": beneficiary_type,
        "home_status": home_status,
        "priority_code": priority_code,
        "priority_label": priority_label,
        "status_bucket": status_bucket,
        "sort_rank": sort_rank,
        "overdue_days": overdue_days,
        "due_today": due_today_flag,
        "upcoming": upcoming_flag,
        "followup_date": next_date_str,
        "primary_reason": primary_reason,
        "reasons": reasons,
        "triggered_rules": triggered_rules,
        "escalation": escalation_info,
        "suggested_action": suggested_action,
        "has_missing_data": has_missing_data,
        "missing_data_items": missing_items,
        "verification_warning": verification_warning,
        "pending_visits_count": len(pending_visits),
        "completed_visits_count": len(completed_visits),
        "pending_visit_ids": [v["id"] for v in pending_visits],
    }


def compute_all_priorities(
    conn: sqlite3.Connection,
    ref_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Load all households from SQLite and return ranked priority list + summary."""
    today = ref_date or date.today()
    flag_messages = _load_flag_messages(conn)

    homes = [dict(r) for r in conn.execute("SELECT * FROM home_records ORDER BY beneficiary_id ASC").fetchall()]
    pregs = {r["beneficiary_id"]: dict(r) for r in conn.execute("SELECT * FROM pregnancies").fetchall()}
    children = {r["beneficiary_id"]: dict(r) for r in conn.execute("SELECT * FROM children").fetchall()}
    all_visits = [dict(r) for r in conn.execute("SELECT * FROM visits").fetchall()]

    visits_by_ben: Dict[str, List[Dict[str, Any]]] = {}
    for v in all_visits:
        visits_by_ben.setdefault(v["beneficiary_id"], []).append(v)

    evaluated: List[Dict[str, Any]] = []
    for h in homes:
        bid = h["beneficiary_id"]
        item = evaluate_household_priority(
            home=h,
            preg=pregs.get(bid),
            child=children.get(bid),
            visits=visits_by_ben.get(bid, []),
            flag_messages=flag_messages,
            ref_date=today,
        )
        evaluated.append(item)

    # Stable deterministic sort:
    # 1. priority sort_rank (RED=0, ORANGE=1, OVERDUE=2, DUE_TODAY=3, UPCOMING=4, ROUTINE=5)
    # 2. overdue_days descending
    # 3. has_missing_data descending (missing data surfaced above complete routine)
    # 4. earliest followup_date ascending
    # 5. beneficiary_id ascending
    evaluated.sort(
        key=lambda x: (
            x["sort_rank"],
            -x["overdue_days"],
            0 if x["has_missing_data"] else 1,
            x["followup_date"] or "9999-12-31",
            x["beneficiary_id"],
        )
    )

    summary = {
        "total_households": len(evaluated),
        "immediate_escalation": sum(1 for x in evaluated if x["status_bucket"] == "immediate_escalation"),
        "high_priority": sum(1 for x in evaluated if x["status_bucket"] == "high_priority"),
        "overdue": sum(1 for x in evaluated if x["status_bucket"] == "overdue"),
        "due_today": sum(1 for x in evaluated if x["status_bucket"] == "due_today"),
        "upcoming": sum(1 for x in evaluated if x["status_bucket"] == "upcoming"),
        "routine": sum(1 for x in evaluated if x["status_bucket"] == "routine"),
        "missing_data": sum(1 for x in evaluated if x["has_missing_data"]),
        "reference_date": today.isoformat(),
    }

    return {
        "summary": summary,
        "households": evaluated,
        "rules_config": {
            "emergency_flags": sorted(PRIORITY_RULES_CONFIG["emergency_flags"]),
            "high_priority_flags": sorted(PRIORITY_RULES_CONFIG["high_priority_flags"]),
            "moderate_flags": sorted(PRIORITY_RULES_CONFIG["moderate_flags"]),
            "upcoming_window_days": PRIORITY_RULES_CONFIG["upcoming_window_days"],
            "escalation_disclaimer": PRIORITY_RULES_CONFIG["escalation_disclaimer"],
        },
        "unvalidated_placeholders": UNVALIDATED_RULE_PLACEHOLDERS,
    }
