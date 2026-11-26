"""SAKHI — Voice Processing, Entity Extraction & Conversational Correction Service.

Extracts structured fields from natural ASHA worker transcripts (English, Hindi,
Kannada, or code-mixed) without inventing unmentioned clinical/personal data.
"""

from datetime import date, timedelta
import re
from typing import Any, Dict, List, Optional


WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}

EMERGENCY_TERMS = [
    "vaginal bleeding", "heavy bleeding", "bleeding", "unconscious", "convulsion",
    "seizure", "fits", "severe dizziness", "blurred vision", "not breathing",
    "chest pain", "severe headache", "high fever",
]

BLOOD_GROUP_RE = re.compile(r"\b(AB|A|B|O)\s*(positive|negative|\+|\-)\b", re.IGNORECASE)


def _extract_name(text: str) -> Optional[str]:
    patterns = [
        r"(?i:register|add|visit to|for|mark|schedule (?:a )?follow[- ]?up for|why is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?i:name is|called)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]
    skip_words = {"She", "He", "Her", "His", "The", "Ward", "Today", "Tomorrow", "Next", "This", "All"}
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            candidate = m.group(1).strip()
            if candidate.split()[0] not in skip_words:
                return candidate
    return None


def _extract_address(text: str) -> Optional[str]:
    m = re.search(
        r"(?:lives in|living in|address is|from|ward|sector|village|colony)\s*[:\-]?\s*([A-Za-z0-9\s,.-]{2,45}?)(?=,|\.|weighs|weight|blood|she|he|his|her|and|iron|vaccination|$)",
        text,
        re.IGNORECASE,
    )
    if m:
        val = m.group(0).strip(" ,.")
        val = re.sub(r"^(?:lives in|living in|address is|from)\s+", "", val, flags=re.IGNORECASE).strip(" ,.")
        if val:
            return val.title() if val.lower().startswith("ward") else val
    return None


def _extract_weight(text: str) -> Optional[float]:
    m = re.search(r"(?:weighs|weight(?:\s+to|\s+is)?)\s*(\d+(?:\.\d+)?)\s*(?:kg|kilos?|kilograms?)?", text, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilos?|kilograms?)\b", text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def _extract_age_years(text: str) -> Optional[int]:
    m = re.search(r"(\d{1,2})\s*(?:years?|yrs?)\s*(?:old)?", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\bage(?:\s+is)?\s*[:\-]?\s*(\d{1,2})\b", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _extract_age_months(text: str) -> Optional[int]:
    m = re.search(r"(\d{1,2})\s*(?:months?|mos?)\s*(?:old)?", text, re.IGNORECASE)
    if m and "pregnant" not in text[max(0, m.start() - 20):m.end() + 20].lower():
        return int(m.group(1))
    return None


def _extract_pregnancy_weeks(text: str) -> Optional[int]:
    m_wk = re.search(r"(\d{1,2})\s*(?:weeks?|wks?)\s*(?:pregnant)?", text, re.IGNORECASE)
    if m_wk and ("pregnant" in text.lower() or "pregnancy" in text.lower() or "anc" in text.lower()):
        return int(m_wk.group(1))

    m_mo = re.search(r"(?:(\d{1,2})|(" + "|".join(WORD_NUMBERS.keys()) + r"))\s*months?\s*(?:pregnant|pregnancy)?", text, re.IGNORECASE)
    if m_mo and ("pregnant" in text.lower() or "pregnancy" in text.lower()):
        num = int(m_mo.group(1)) if m_mo.group(1) else WORD_NUMBERS.get(m_mo.group(2).lower(), 0)
        if 1 <= num <= 10:
            return num * 4
    return None


def _extract_blood_group(text: str) -> Optional[str]:
    m = BLOOD_GROUP_RE.search(text)
    if not m:
        return None
    grp = m.group(1).upper()
    rh = "+" if m.group(2).lower() in ("positive", "+") else "-"
    return f"{grp}{rh}"


def _extract_phone(text: str) -> Optional[str]:
    m = re.search(r"\b(\d{10})\b", text)
    return m.group(1) if m else None


def _extract_iron_status(text: str) -> Optional[str]:
    low = text.lower()
    if "iron" in low or "ifa" in low:
        if any(w in low for w in ("irregular", "missed", "not taking", "skipped")):
            return "Irregular"
        if any(w in low for w in ("regular", "regularly", "daily", "taking")):
            return "Regular"
    return None


def resolve_relative_date(text: str, ref_date: Optional[date] = None) -> Dict[str, Any]:
    """Resolve clear relative date phrases; flag ambiguous phrases for confirmation."""
    today = ref_date or date.today()
    low = text.lower()

    m_iso = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if m_iso:
        return {"date": m_iso.group(1), "ambiguous": False}

    if "today" in low:
        return {"date": today.isoformat(), "ambiguous": False}
    if "tomorrow" in low:
        return {"date": (today + timedelta(days=1)).isoformat(), "ambiguous": False}
    if "next week" in low:
        return {"date": (today + timedelta(days=7)).isoformat(), "ambiguous": False}

    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for idx, day_name in enumerate(weekdays):
        if day_name in low:
            days_ahead = (idx - today.weekday()) % 7
            if days_ahead == 0 or "next" in low:
                days_ahead = days_ahead or 7
            return {"date": (today + timedelta(days=days_ahead)).isoformat(), "ambiguous": False}

    if any(w in low for w in ("soon", "later", "sometime", "few days")):
        return {"date": None, "ambiguous": True, "clarification": "Please specify the exact follow-up date (e.g. tomorrow, next Monday, or YYYY-MM-DD)."}

    return {"date": None, "ambiguous": False}


def detect_emergency_indicators(text: str) -> Optional[Dict[str, Any]]:
    low = (text or "").lower()
    matched = [term for term in EMERGENCY_TERMS if term in low]
    if not matched:
        return None
    return {
        "emergency_detected": True,
        "matched_indicators": matched,
        "warning": "POTENTIAL DANGER SIGN MENTIONED — ESCALATE IMMEDIATELY",
        "instruction": (
            "Do not wait for AI processing or scheduled visits. "
            "Contact ANM / Primary Health Centre Medical Officer or arrange immediate referral per NHM protocol. "
            "SAKHI does not diagnose emergencies."
        ),
    }


def parse_voice_transcript(
    transcript: str,
    context_screen: str = "home",
    current_draft: Optional[Dict[str, Any]] = None,
    beneficiary_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse transcript into structured intent, entities, corrections, or clarification."""
    text = (transcript or "").strip()
    low = text.lower()

    if not text or len(text) < 3:
        return {
            "intent": "clarification_needed",
            "clarification": "I could not hear a clear request. Please speak your request or beneficiary details again.",
            "original_transcript": text,
        }

    emergency = detect_emergency_indicators(text)

    # 1. Cancel / Confirm conversational commands when a draft is open
    if current_draft:
        if any(p in low for p in ("cancel registration", "cancel this", "discard", "never mind")):
            return {
                "intent": "cancel_draft",
                "message": "Draft cancelled. No changes were saved.",
                "original_transcript": text,
                "emergency": emergency,
            }
        if any(p in low for p in ("save the beneficiary", "confirm and save", "save it", "yes confirm", "confirm save")):
            return {
                "intent": "confirm_draft",
                "draft": current_draft,
                "original_transcript": text,
                "emergency": emergency,
            }

        # Conversational corrections to an active registration draft
        if any(p in low for p in ("change", "not ", "actually", "update her", "update his", "correct")):
            updated = dict(current_draft)
            changes: List[str] = []
            w = _extract_weight(text)
            if w is not None:
                updated["weight"] = f"{w} kg" if updated.get("entity_type") == "mother" else w
                changes.append(f"weight -> {w} kg")
            addr = _extract_address(text)
            if addr:
                updated["address"] = addr
                changes.append(f"address -> {addr}")
            wks = _extract_pregnancy_weeks(text)
            if wks is not None:
                updated["weeks"] = wks
                changes.append(f"pregnancy -> {wks} weeks")
            age = _extract_age_years(text)
            if age is not None:
                updated["age"] = age
                changes.append(f"age -> {age}")
            bg = _extract_blood_group(text)
            if bg:
                updated["bloodGroup"] = bg
                changes.append(f"bloodGroup -> {bg}")
            iron = _extract_iron_status(text)
            if iron:
                updated["ironStatus"] = iron
                changes.append(f"ironStatus -> {iron}")

            if changes:
                return {
                    "intent": "correct_draft",
                    "draft": updated,
                    "changes": changes,
                    "original_transcript": text,
                    "emergency": emergency,
                }

    # 2. Priority Dashboard Queries (skip if clearly an action command like mark/schedule/reschedule/cancel)
    is_action_verb = low.startswith(("mark ", "schedule ", "reschedule ", "cancel ", "complete "))
    if not is_action_verb and any(p in low for p in (
        "which households", "need attention", "overdue households", "why is",
        "why prioritized", "pending follow-up", "vaccination follow-up",
        "next five priority", "next 5 priority", "not been visited", "priority households"
    )):
        return {
            "intent": "priority_query",
            "query": text,
            "target_name": _extract_name(text),
            "beneficiary_id": beneficiary_id,
            "original_transcript": text,
            "emergency": emergency,
        }

    # 3. Beneficiary Registration (Mother vs Child) — supports explicit "register" and natural phrases (skip questions like "how many ... registered")
    is_question = low.startswith(("how many", "which", "what", "who", "show")) or "are registered" in low
    has_reg_verb = (not is_question) and (
        bool(re.search(r"\bregister\b", low))
        or any(w in low for w in ("new mother", "new child", "new baby", "add mother", "add baby", "add child"))
    )
    has_natural_mother = bool(re.search(r"\b(mother\s+name\s+is|pregnant\s+woman\s+named)\b", low))
    has_natural_child = bool(re.search(r"\b(child\s+named|baby\s+named|child\s+name\s+is)\b", low))
    if has_reg_verb or has_natural_mother or has_natural_child:
        is_child = (has_natural_child or any(w in low for w in ("child", "baby", "boy", "girl", "months old", "vaccination status"))) and "pregnant" not in low and not has_natural_mother
        name = _extract_name(text)
        if not name:
            m_nm = re.search(r"(?i:mother\s+name\s+is|child\s+name\s+is|pregnant\s+woman\s+named|child\s+named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
            if m_nm:
                name = m_nm.group(1).strip()
        address = _extract_address(text)
        weight = _extract_weight(text)
        phone = _extract_phone(text)

        if is_child:
            age_mo = _extract_age_months(text)
            age_yr = _extract_age_years(text)
            age_str = f"{age_mo} months" if age_mo is not None else (f"{age_yr} years" if age_yr is not None else None)
            vac_note = "Incomplete" if "incomplete" in low else ("Due" if "due" in low else None)
            fields = {
                "entity_type": "child",
                "name": name,
                "age": age_str,
                "address": address,
                "weight": weight,
                "phone": phone,
                "bloodGroup": _extract_blood_group(text),
                "vaccinationStatus": vac_note,
            }
            return {
                "intent": "register_child",
                "fields": fields,
                "original_transcript": text,
                "emergency": emergency,
            }

        # Pregnant mother registration
        fields = {
            "entity_type": "mother",
            "name": name,
            "age": _extract_age_years(text),
            "address": address,
            "weeks": _extract_pregnancy_weeks(text),
            "weight": f"{weight} kg" if weight is not None else None,
            "bloodGroup": _extract_blood_group(text),
            "ironStatus": _extract_iron_status(text),
            "phone": phone,
            "dueDate": resolve_relative_date(text).get("date"),
        }
        return {
            "intent": "register_mother",
            "fields": fields,
            "original_transcript": text,
            "emergency": emergency,
        }

    # 4. Follow-up Automation (Complete / Reschedule / Cancel / Schedule)
    if any(p in low for p in ("mark ", "completed", "complete the visit", "complete follow")) and not low.startswith("show"):
        return {
            "intent": "complete_followup",
            "target_name": _extract_name(text),
            "beneficiary_id": beneficiary_id,
            "original_transcript": text,
            "emergency": emergency,
        }

    if "reschedule" in low:
        dt = resolve_relative_date(text)
        return {
            "intent": "reschedule_followup",
            "target_name": _extract_name(text),
            "beneficiary_id": beneficiary_id,
            "due_date": dt.get("date"),
            "date_ambiguous": dt.get("ambiguous"),
            "clarification": dt.get("clarification"),
            "original_transcript": text,
            "emergency": emergency,
        }

    if "cancel" in low and ("follow-up" in low or "followup" in low or "visit" in low):
        return {
            "intent": "cancel_followup",
            "target_name": _extract_name(text),
            "beneficiary_id": beneficiary_id,
            "original_transcript": text,
            "emergency": emergency,
        }

    if "schedule" in low and ("follow-up" in low or "followup" in low) and "visit to" not in low:
        dt = resolve_relative_date(text)
        return {
            "intent": "schedule_followup",
            "target_name": _extract_name(text),
            "beneficiary_id": beneficiary_id,
            "due_date": dt.get("date") or (date.today() + timedelta(days=7)).isoformat() if not dt.get("ambiguous") else None,
            "date_ambiguous": dt.get("ambiguous"),
            "clarification": dt.get("clarification"),
            "note": text,
            "original_transcript": text,
            "emergency": emergency,
        }

    # 5. Visit Documentation
    if any(p in low for p in ("visit to", "record a visit", "record the visit", "plan a visit", "plan visits", "home visit")):
        dt = resolve_relative_date(text)
        has_followup_req = "follow-up" in low or "followup" in low
        followup_date = (date.today() + timedelta(days=7)).isoformat() if ("next week" in low and has_followup_req) else dt.get("date")
        visit_type = "ANC" if ("anc" in low or "iron" in low or "pregnant" in low) else ("Vaccination" if "vaccin" in low else "GENERAL")
        flag = "S" if emergency else ("M" if any(w in low for w in ("irregular", "fever", "cough", "pain", "missed")) else "N")
        return {
            "intent": "record_visit",
            "target_name": _extract_name(text),
            "beneficiary_id": beneficiary_id,
            "visit_type": visit_type,
            "due_date": dt.get("date") or date.today().isoformat(),
            "followup_requested": has_followup_req,
            "followup_date": followup_date,
            "note": text,
            "flag": flag,
            "original_transcript": text,
            "emergency": emergency,
        }

    # 6. Fallback -> Grounded AI Chatbot
    return {
        "intent": "chatbot_query",
        "query": text,
        "beneficiary_id": beneficiary_id,
        "original_transcript": text,
        "emergency": emergency,
    }
