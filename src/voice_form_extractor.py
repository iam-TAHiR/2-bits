"""SAKHI — Universal Form-Schema Voice Extractor.

Maps natural-language transcripts directly to the active SAKHI frontend form
context (exact DOM field IDs, types, dropdown options, and required fields)
without inventing unmentioned values.
"""

from datetime import date, datetime, timedelta
import re
import sqlite3
from typing import Any, Dict, List, Optional

try:
    from src.voice_service import (
        _extract_address,
        _extract_age_years,
        _extract_blood_group,
        _extract_iron_status,
        _extract_phone,
        _extract_pregnancy_weeks,
        _extract_weight,
        detect_emergency_indicators,
        resolve_relative_date,
    )
    from src.voice_action_service import _find_beneficiary
except ImportError:
    from voice_service import (
        _extract_address,
        _extract_age_years,
        _extract_blood_group,
        _extract_iron_status,
        _extract_phone,
        _extract_pregnancy_weeks,
        _extract_weight,
        detect_emergency_indicators,
        resolve_relative_date,
    )
    from voice_action_service import _find_beneficiary

try:
    from src.multilingual_nlp import detect_script_language, extract_indic_fields
    from src.sarvam_service import SarvamSpeechService
except ImportError:
    from multilingual_nlp import detect_script_language, extract_indic_fields
    from sarvam_service import SarvamSpeechService

_sarvam_translate_client = SarvamSpeechService()


MONTH_NAMES = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}


def _parse_natural_date(text: str, ref_date: Optional[date] = None) -> Optional[date]:
    """Parse explicit natural dates like 'March 15', '12 August 2025', '15/03/2026', '2026-03-15'."""
    today = ref_date or date.today()

    m_iso = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m_iso:
        try:
            return date(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))
        except ValueError:
            pass

    m_dmy = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", text)
    if m_dmy:
        try:
            return date(int(m_dmy.group(3)), int(m_dmy.group(2)), int(m_dmy.group(1)))
        except ValueError:
            pass

    month_pat = "|".join(MONTH_NAMES.keys())
    # "12 August 2025" or "12 August"
    m1 = re.search(rf"\b(\d{{1,2}})\s+({month_pat})(?:\s+(\d{{4}}))?\b", text, re.IGNORECASE)
    if m1:
        day = int(m1.group(1))
        mon = MONTH_NAMES[m1.group(2).lower()]
        yr = int(m1.group(3)) if m1.group(3) else today.year
        try:
            d = date(yr, mon, day)
            if not m1.group(3) and d > today:
                d = date(yr - 1, mon, day)
            return d
        except ValueError:
            pass

    # "March 15, 2026" or "March 15"
    m2 = re.search(rf"\b({month_pat})\s+(\d{{1,2}})(?:,?\s+(\d{{4}}))?\b", text, re.IGNORECASE)
    if m2:
        mon = MONTH_NAMES[m2.group(1).lower()]
        day = int(m2.group(2))
        yr = int(m2.group(3)) if m2.group(3) else today.year
        try:
            d = date(yr, mon, day)
            if not m2.group(3) and d > today:
                d = date(yr - 1, mon, day)
            return d
        except ValueError:
            pass

    return None


def _extract_person_name_for_form(text: str) -> Optional[str]:
    patterns = [
        r"(?i:her name is|his name is|name is|child named|named|register(?: a child named)?|for|visited|visit to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]
    skip = {"She", "He", "Her", "His", "The", "Ward", "Today", "Tomorrow", "Child", "Mother"}
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            cand = m.group(1).strip()
            if cand.split()[0] not in skip:
                return cand
    return None


def _extract_guardian_name(text: str) -> Optional[str]:
    m = re.search(
        r"(?i:(?:mother(?:'s)? name is|father(?:'s)? name is|guardian(?:'s)? name is|parent(?:'s)? name is|mother is|father is))\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        text,
    )
    return m.group(1).strip() if m else None


def _extract_gender(text: str) -> Optional[str]:
    low = text.lower()
    if re.search(r"\b(male|boy|son)\b", low):
        return "Male"
    if re.search(r"\b(female|girl|daughter)\b", low):
        return "Female"
    return None


def _extract_in_n_days(text: str, ref_date: Optional[date] = None) -> Optional[date]:
    today = ref_date or date.today()
    word_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "ten": 10}
    m = re.search(r"\bin\s+(\d+|" + "|".join(word_map.keys()) + r")\s+days?\b", text, re.IGNORECASE)
    if m:
        raw = m.group(1).lower()
        days = int(raw) if raw.isdigit() else word_map.get(raw, 0)
        if days > 0:
            return today + timedelta(days=days)
    return None


def extract_for_form_context(
    transcript: str,
    form_context: Dict[str, Any],
    conn: sqlite3.Connection,
    ref_date: Optional[date] = None,
    language_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract explicitly spoken values mapped to the active frontend form schema.

    Supports English, Kannada, Hindi, and code-mixed speech:
    1. Preserves original_transcript.
    2. Detects script/language.
    3. Runs native Indic extraction directly on original_transcript.
    4. When non-English and Sarvam Translate (mayura:v1) is available, translates
       to English (retaining translated_transcript) and merges any additional fields.
    """
    original_text = (transcript or "").strip()
    today = ref_date or date.today()

    form_id = form_context.get("form_id") or "general"
    form_name = form_context.get("form_name") or form_id
    schema_fields: List[Dict[str, Any]] = form_context.get("fields") or []
    ben_id_ctx = form_context.get("beneficiary_id")

    detected_lang = detect_script_language(original_text, hint=language_hint)
    translated_text: Optional[str] = None
    indic_extracted: Dict[str, Any] = {}

    if detected_lang != "en-IN":
        indic_extracted = extract_indic_fields(original_text, form_id=form_id, ref_date=today)
        if _sarvam_translate_client.is_configured():
            t_res = _sarvam_translate_client.translate_text(
                original_text,
                source_language_code=detected_lang,
                target_language_code="en-IN",
            )
            if t_res.get("success") and t_res.get("translated_text"):
                translated_text = t_res["translated_text"]

    # Run English extraction on translated text (if available) or original text
    text = translated_text or original_text
    low = text.lower()

    extracted: Dict[str, Any] = dict(indic_extracted)
    uncertain: List[str] = []
    unmapped: List[str] = []
    notes_meta: List[str] = []
    candidate_beneficiaries: List[Dict[str, Any]] = []
    clarification: Optional[str] = None

    # 1. Maternal / Pregnancy Registration Form (#maternalProfileForm)
    if form_id == "maternalProfileForm":
        name = _extract_person_name_for_form(text)
        if name:
            extracted["motherFormName"] = name

        age = _extract_age_years(text)
        if age is not None:
            if 12 <= age <= 60:
                extracted["motherFormAge"] = age
            else:
                uncertain.append(f"Age '{age}' looks out of maternal range (12-60)")

        phone = _extract_phone(text)
        if phone:
            extracted["motherFormPhone"] = phone

        addr = _extract_address(text)
        if addr:
            extracted["motherFormAddress"] = addr

        # DOB vs LMP
        if any(k in low for k in ("last menstrual period", "lmp")):
            lmp_d = _parse_natural_date(text, ref_date=today)
            if lmp_d:
                edd = lmp_d + timedelta(days=280)
                extracted["motherFormDueDate"] = edd.strftime("%d %b %Y")
                notes_meta.append(f"EDD calculated from LMP ({lmp_d.isoformat()}) + 280 days")
            else:
                uncertain.append("LMP mentioned without a clear date")
        else:
            due_res = resolve_relative_date(text, ref_date=today)
            if due_res.get("date") and "due" in low:
                d_obj = date.fromisoformat(due_res["date"])
                extracted["motherFormDueDate"] = d_obj.strftime("%d %b %Y")

        if any(k in low for k in ("born on", "date of birth", "dob")):
            dob_d = _parse_natural_date(text, ref_date=today)
            if dob_d:
                extracted["motherFormDOB"] = dob_d.strftime("%d/%m/%Y")

        w = _extract_weight(text)
        if w is not None:
            if 25 <= w <= 150:
                extracted["motherFormWeight"] = f"{w:g} kg"
            else:
                uncertain.append(f"Weight '{w} kg' looks unusual; please verify")

        iron = _extract_iron_status(text)
        if iron:
            extracted["motherFormIron"] = iron

        bg = _extract_blood_group(text)
        if bg:
            extracted["motherFormBlood"] = bg

    # 2. Child Registration Form (#babyProfileForm)
    elif form_id == "babyProfileForm":
        name = _extract_person_name_for_form(text)
        if name:
            extracted["babyFormName"] = name

        gender = _extract_gender(text)
        if gender:
            extracted["babyFormGender"] = gender

        if any(k in low for k in ("born on", "date of birth", "dob", "birth")):
            dob_d = _parse_natural_date(text, ref_date=today)
            if dob_d:
                if dob_d > today:
                    uncertain.append(f"DOB {dob_d.isoformat()} is in the future")
                else:
                    extracted["babyFormDOB"] = dob_d.strftime("%d/%m/%Y")
            else:
                uncertain.append("Date of birth mentioned but could not parse exact date")

        phone = _extract_phone(text)
        if phone:
            extracted["babyFormPhone"] = phone

        addr = _extract_address(text)
        if addr:
            extracted["babyFormAddress"] = addr

        guardian = _extract_guardian_name(text)
        if guardian:
            extracted["babyFormGuardian"] = guardian

        bg = _extract_blood_group(text)
        if bg:
            extracted["babyFormBlood"] = bg

    # 3. Visit / Follow-up Form (#planVisitForm or Visits / Follow-ups screens)
    elif form_id in ("planVisitForm", "visitsRegister", "followupsRegister", "householdDetail"):
        # Match beneficiary
        spoken_name = _extract_person_name_for_form(text)
        matches = _find_beneficiary(conn, spoken_name, ben_id_ctx)
        if len(matches) == 1:
            extracted["planVisitBenId"] = matches[0]["beneficiary_id"]
            extracted["beneficiary_name"] = matches[0]["display_name"]
        elif len(matches) > 1:
            candidate_beneficiaries = matches
            clarification = (
                "Multiple beneficiaries matched: "
                + ", ".join(f"{m['display_name']} ({m['beneficiary_id']})" for m in matches)
                + ". Please select one."
            )
        elif spoken_name:
            uncertain.append(f"No existing record matched '{spoken_name}'; please select household manually")

        # Visit / Follow-up Type mapped to exact <select id="planVisitType"> options
        if any(k in low for k in ("antenatal", "anc", "pregnant")):
            extracted["planVisitType"] = "ANC"
        elif any(k in low for k in ("postnatal", "pnc", "postpartum")):
            extracted["planVisitType"] = "PNC"
        elif any(k in low for k in ("vaccin", "immuniz")):
            extracted["planVisitType"] = "Vaccination"
        elif "high risk" in low or "high-risk" in low:
            extracted["planVisitType"] = "HIGH_RISK"
        elif "visit" in low or "follow-up" in low or "followup" in low:
            extracted["planVisitType"] = "GENERAL"

        # Follow-up Due Date (YYYY-MM-DD for <input type="date" id="planVisitDueDate">)
        in_days = _extract_in_n_days(text, ref_date=today)
        if in_days:
            extracted["planVisitDueDate"] = in_days.isoformat()
        else:
            dt = resolve_relative_date(text, ref_date=today)
            if dt.get("date"):
                extracted["planVisitDueDate"] = dt["date"]
            elif dt.get("ambiguous"):
                uncertain.append("Follow-up date phrase is ambiguous; please pick exact date")

        # Note / Observations (preserve exact BP, symptoms, feeling better without over-diagnosing)
        extracted["planVisitNote"] = text

        # Flag: avoid treating casual past symptom ("dizziness yesterday, feeling better today") as emergency
        casual_resolved = "feeling better" in low or "better today" in low
        emergency = None if casual_resolved else detect_emergency_indicators(text)
        if emergency:
            extracted["planVisitFlag"] = "S"
        elif "high risk" in low or "high-risk" in low:
            extracted["planVisitFlag"] = "H"
        else:
            extracted["planVisitFlag"] = "N"

    # Compute missing required fields by merging current DOM values + newly extracted values
    missing_fields: List[str] = []
    for f in schema_fields:
        fid = f.get("id")
        if not fid:
            continue
        is_req = bool(f.get("required"))
        cur_val = str(f.get("current_value") or "").strip()
        new_val = str(extracted.get(fid) or "").strip()
        if is_req and not (new_val or cur_val):
            missing_fields.append(f.get("label") or fid)

    filled_labels = [
        next((f.get("label") or fid for f in schema_fields if f.get("id") == fid), fid)
        for fid in extracted
        if fid not in ("planVisitBenId", "beneficiary_name")
    ]
    if filled_labels:
        tts_summary = f"{', '.join(filled_labels)} have been filled."
        if missing_fields:
            tts_summary += f" {', '.join(missing_fields)} still missing."
    else:
        tts_summary = "No matching fields were extracted. Please speak clearly or edit fields manually."

    return {
        "success": True,
        "form_context": form_id,
        "form_name": form_name,
        "language_code": detected_lang,
        "original_transcript": original_text,
        "translated_transcript": translated_text,
        "fields": extracted,
        "missing_fields": missing_fields,
        "uncertain_fields": uncertain,
        "unmapped_information": unmapped,
        "notes_meta": notes_meta,
        "candidate_beneficiaries": candidate_beneficiaries,
        "clarification": clarification,
        "requires_confirmation": True,
        "tts_summary": tts_summary,
    }
