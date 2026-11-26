"""SAKHI — Multilingual NLP, Script Detection, Transliteration & Indic Field Extraction.

Supports Kannada (kn-IN), Hindi (hi-IN), and English (en-IN) transcripts.
Preserves original transcript and optionally uses Sarvam Translate (mayura:v1)
while providing deterministic native Kannada/Hindi extraction as well.
"""

from datetime import date, timedelta
import re
from typing import Any, Dict, Optional, Tuple


KANNADA_MONTHS = {
    "ಜನವರಿ": 1, "ಫೆಬ್ರವರಿ": 2, "ಮಾರ್ಚ್": 3, "ಏಪ್ರಿಲ್": 4,
    "ಮೇ": 5, "ಜೂನ್": 6, "ಜುಲೈ": 7, "ಆಗಸ್ಟ್": 8,
    "ಸೆಪ್ಟೆಂಬರ್": 9, "ಅಕ್ಟೋಬರ್": 10, "ನವೆಂಬರ್": 11, "ಡಿಸೆಂಬರ್": 12,
}

HINDI_MONTHS = {
    "जनवरी": 1, "फरवरी": 2, "मार्च": 3, "अप्रैल": 4,
    "मई": 5, "जून": 6, "जुलाई": 7, "अगस्त": 8,
    "सितंबर": 9, "अक्टूबर": 10, "नवंबर": 11, "दिसंबर": 12,
}

KANNADA_ORDINALS = {
    "ಒಂದನೇ": 1, "ಎರಡನೇ": 2, "ಮೂರನೇ": 3, "ನಾಲ್ಕನೇ": 4, "ಐದನೇ": 5,
    "ಆರನೇ": 6, "ಏಳನೇ": 7, "ಎಂಟನೇ": 8, "ಒಂಬತ್ತನೇ": 9, "ಹತ್ತನೇ": 10,
    "ಹನ್ನೊಂದನೇ": 11, "ಹನ್ನೆರಡನೇ": 12, "ಹದಿಮೂರನೇ": 13, "ಹದಿನಾಲ್ಕನೇ": 14,
}

HINDI_ORDINALS = {
    "पहला": 1, "दूसरा": 2, "तीसरा": 3, "चौथा": 4, "पांचवा": 5,
    "छठा": 6, "सातवां": 7, "आठवां": 8, "नौवां": 9, "दसवां": 10,
    "बारहवां": 12,
}

# Lightweight Kannada Unicode -> Latin transliteration for proper names
_KN_CONSONANTS = {
    "ಕ": "k", "ಖ": "kh", "ಗ": "g", "ಘ": "gh", "ಙ": "ng",
    "ಚ": "ch", "ಛ": "chh", "ಜ": "j", "ಝ": "jh", "ಞ": "ny",
    "ಟ": "t", "ಠ": "th", "ಡ": "d", "ಢ": "dh", "ಣ": "n",
    "ತ": "t", "ಥ": "th", "ದ": "d", "ಧ": "dh", "ನ": "n",
    "ಪ": "p", "ಫ": "ph", "ಬ": "b", "ಭ": "bh", "ಮ": "m",
    "ಯ": "y", "ರ": "r", "ಲ": "l", "ವ": "v", "ಶ": "sh",
    "ಷ": "sh", "ಸ": "s", "ಹ": "h", "ಳ": "l",
}
_KN_VOWELS = {
    "ಅ": "a", "ಆ": "a", "ಇ": "i", "ಈ": "i", "ಉ": "u", "ಊ": "u",
    "ಋ": "ri", "ಎ": "e", "ಏ": "e", "ಐ": "ai", "ಒ": "o", "ಓ": "o", "ಔ": "au",
}
_KN_MATRAS = {
    "ಾ": "a", "ಿ": "i", "ೀ": "i", "ು": "u", "ೂ": "u",
    "ೃ": "ri", "ೆ": "e", "ೇ": "e", "ೈ": "ai", "ೊ": "o", "ೋ": "o", "ೌ": "au",
    "್": "",
}
_KN_SIGNS = {"ಂ": "m", "ಃ": "h"}


def detect_script_language(text: str, hint: Optional[str] = None) -> str:
    """Detect script language (kn-IN, hi-IN, or en-IN)."""
    if hint in ("kn-IN", "hi-IN", "en-IN"):
        # Still verify if actual script contradicts hint
        if any("\u0C80" <= ch <= "\u0CFF" for ch in text):
            return "kn-IN"
        if any("\u0900" <= ch <= "\u097F" for ch in text):
            return "hi-IN"
        return hint
    if any("\u0C80" <= ch <= "\u0CFF" for ch in text):
        return "kn-IN"
    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "hi-IN"
    return "en-IN"


def transliterate_kannada_to_latin(text: str) -> str:
    """Convert Kannada script proper names (e.g. ರೋಹನ್ ಕುಮಾರ್) to Title Case Latin."""
    if not text or not any("\u0C80" <= ch <= "\u0CFF" for ch in text):
        return text
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in _KN_VOWELS:
            out.append(_KN_VOWELS[ch])
        elif ch in _KN_CONSONANTS:
            base = _KN_CONSONANTS[ch]
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt in _KN_MATRAS:
                out.append(base + _KN_MATRAS[nxt])
                i += 1
            else:
                # Inherent 'a' unless at word end and word > 1 char
                is_word_end = (i + 1 == n) or (text[i + 1] in " ,.")
                out.append(base if (is_word_end and len(out) > 0) else base + "a")
        elif ch in _KN_SIGNS:
            out.append(_KN_SIGNS[ch])
        else:
            out.append(ch)
        i += 1
    res = "".join(out)
    # Clean common suffixes like 'kshm' -> 'kshmi' when ಿ was handled
    return " ".join(w.capitalize() for w in res.split() if w)


def _clean_kn_name(raw: str) -> str:
    s = raw.strip(" ,.।")
    return transliterate_kannada_to_latin(s) if any("\u0C80" <= c <= "\u0CFF" for c in s) else s


def extract_indic_date(text: str, ref_date: Optional[date] = None) -> Optional[date]:
    """Parse Kannada or Hindi dates such as '2025 ಆಗಸ್ಟ್ 12ರಂದು' or '12 अगस्त 2025'."""
    today = ref_date or date.today()
    all_months = {**KANNADA_MONTHS, **HINDI_MONTHS}
    m_pat = "|".join(re.escape(k) for k in all_months.keys())

    # Pattern 1: YYYY <Month> DD (e.g. 2025 ಆಗಸ್ಟ್ 12ರಂದು)
    m1 = re.search(rf"(\d{{4}})\s+({m_pat})\s+(\d{{1,2}})", text)
    if m1:
        try:
            return date(int(m1.group(1)), all_months[m1.group(2)], int(m1.group(3)))
        except ValueError:
            pass

    # Pattern 2: DD <Month> YYYY (e.g. 12 ಆಗಸ್ಟ್ 2025)
    m2 = re.search(rf"(\d{{1,2}})\s+({m_pat})(?:\s+(\d{{4}}))?", text)
    if m2:
        yr = int(m2.group(3)) if m2.group(3) else today.year
        try:
            d = date(yr, all_months[m2.group(2)], int(m2.group(1)))
            if not m2.group(3) and d > today:
                d = date(yr - 1, all_months[m2.group(2)], int(m2.group(1)))
            return d
        except ValueError:
            pass

    # Pattern 3: <Month> DD [YYYY]
    m3 = re.search(rf"({m_pat})\s+(\d{{1,2}})(?:\s+(\d{{4}}))?", text)
    if m3:
        yr = int(m3.group(3)) if m3.group(3) else today.year
        try:
            d = date(yr, all_months[m3.group(1)], int(m3.group(2)))
            if not m3.group(3) and d > today:
                d = date(yr - 1, all_months[m3.group(1)], int(m3.group(2)))
            return d
        except ValueError:
            pass

    return None


def extract_indic_fields(text: str, form_id: str, ref_date: Optional[date] = None) -> Dict[str, Any]:
    """Deterministic Kannada & Hindi field extraction mapped directly to form field IDs."""
    today = ref_date or date.today()
    out: Dict[str, Any] = {}

    # 1. Person Name (avoid matching ತಾಯಿಯ ಹೆಸರು / ತಂದೆಯ ಹೆಸರು as child/mother name)
    name: Optional[str] = None
    # Strip guardian clause first when looking for primary person name
    text_no_guardian = re.sub(r"(?:ತಾಯಿಯ|ತಂದೆಯ|ಪೋಷಕರ|माँ का|पिता का)\s*ಹೆಸರು|नाम\s*[^,\.]+", "", text)
    m_kn_name = re.search(
        r"(?:ಅವನ\s+ಹೆಸರು|ಅವಳ\s+ಹೆಸರು|ಮಗುವಿನ\s+ಹೆಸರು|ತಾಯಿಯ\s+ಹೆಸರು|ಹೆಸರು)\s*[:\-]?\s*([^\d,\.\n]{2,35})",
        text_no_guardian if form_id == "babyProfileForm" else text,
    )
    if form_id == "babyProfileForm":
        m_kn_name = re.search(
            r"(?:ಅವನ\s+ಹೆಸರು|ಅವಳ\s+ಹೆಸರು|ಮಗುವಿನ\s+ಹೆಸರು|(?<!ತಾಯಿಯ\s)(?<!ತಂದೆಯ\s)ಹೆಸರು)\s*[:\-]?\s*([^\d,\.\n]{2,35})",
            text,
        )
    if m_kn_name:
        name = _clean_kn_name(m_kn_name.group(1))
    else:
        m_hi_name = re.search(r"(?:उसका\s+नाम|बच्चे\s+का\s+नाम|(?<!माँ\sका\s)(?<!पिता\sका\s)नाम)\s*[:\-]?\s*([^\d,\.\n]{2,35})", text)
        if m_hi_name:
            name = m_hi_name.group(1).strip(" ,.।")

    # 2. Guardian Name (Kannada ತಾಯಿಯ ಹೆಸರು / ತಂದೆಯ ಹೆಸರು, Hindi माँ का नाम / पिता का नाम)
    guardian: Optional[str] = None
    m_g = re.search(r"(?:ತಾಯಿಯ\s+ಹೆಸರು|ತಂದೆಯ\s+ಹೆಸರು|ಪೋಷಕರ\s+ಹೆಸರು|माँ\s+का\s+नाम|पिता\s+का\s+नाम)\s*[:\-]?\s*([^\d,\.\n]{2,35})", text)
    if m_g:
        guardian = _clean_kn_name(m_g.group(1))

    # 3. Address / Ward (Kannada ವಿಳಾಸ / ವಾರ್ಡ್ + ordinals, Hindi पता / वार्ड)
    address: Optional[str] = None
    for ord_word, num in {**KANNADA_ORDINALS, **HINDI_ORDINALS}.items():
        if ord_word in text and ("ವಾರ್ಡ್" in text or "वार्ड" in text or "ward" in text.lower()):
            address = f"Ward {num}"
            break
    if not address:
        m_w = re.search(r"(?:ವಾರ್ಡ್|वार्ड)\s*(\d{1,3})", text)
        if m_w:
            address = f"Ward {m_w.group(1)}"
    if not address:
        m_addr = re.search(r"(?:ವಿಳಾಸ|पता)\s*[:\-]?\s*([^,\.\n]{2,40})", text)
        if m_addr:
            raw_addr = m_addr.group(1).strip()
            raw_addr = re.sub(r"(?:ನಲ್ಲಿ\s+ವಾಸಿಸುತ್ತಾನೆ|ನಲ್ಲಿ\s+ವಾಸಿಸುತ್ತಾಳೆ)$", "", raw_addr).strip()
            address = transliterate_kannada_to_latin(raw_addr) if any("\u0C80" <= c <= "\u0CFF" for c in raw_addr) else raw_addr

    # 4. Date (DOB or LMP)
    indic_d = extract_indic_date(text, ref_date=today)

    # 5. Gender
    gender: Optional[str] = None
    if any(w in text for w in ("ಗಂಡು", "ಅವನು", "ಹುಡುಗ", "लड़का", "पुरुष")):
        gender = "Male"
    elif any(w in text for w in ("ಹೆಣ್ಣು", "ಅವಳು", "ಹುಡುಗಿ", "लड़की", "महिला")):
        gender = "Female"

    # 6. Age, Weight, Phone, Blood Group, Iron
    age_val: Optional[int] = None
    m_age = re.search(r"(\d{1,2})\s*(?:ವರ್ಷ|ಸाल|साल)", text) or re.search(r"(?:ವಯಸ್ಸು|उम्र)\s*[:\-]?\s*(\d{1,2})", text)
    if m_age:
        age_val = int(m_age.group(1))

    weight_val: Optional[float] = None
    m_wt = re.search(r"(?:ತೂಕ|वजन)?\s*(\d+(?:\.\d+)?)\s*(?:ಕೆಜಿ|ಕಿಲೋ|किलो|kg)", text, re.IGNORECASE)
    if m_wt:
        weight_val = float(m_wt.group(1))

    phone_val: Optional[str] = None
    m_ph = re.search(r"\b(\d{10})\b", text)
    if m_ph:
        phone_val = m_ph.group(1)

    bg_val: Optional[str] = None
    m_bg = re.search(r"\b(AB|A|B|O)\s*(ಪಾಸಿಟಿವ್|ನೆಗೆಟಿವ್|पॉजिटिव|नेगेटिव|positive|negative|\+|\-)", text, re.IGNORECASE)
    if m_bg:
        rh = "+" if m_bg.group(2).lower() in ("ಪಾಸಿಟಿವ್", "पॉजिटिव", "positive", "+") else "-"
        bg_val = f"{m_bg.group(1).upper()}{rh}"

    iron_val: Optional[str] = None
    if "ಕಬ್ಬಿಣ" in text or "माತ್ರೆ" in text or "आयरन" in text:
        if "ಅನಿಯಮಿತ" in text or "ತಪ್ಪಿ" in text or "अनियमित" in text:
            iron_val = "Irregular"
        elif "ನಿಯಮಿತ" in text or "नियमित" in text:
            iron_val = "Regular"

    if form_id == "babyProfileForm":
        if name:
            out["babyFormName"] = name
        if gender:
            out["babyFormGender"] = gender
        if indic_d and indic_d <= today:
            out["babyFormDOB"] = indic_d.strftime("%d/%m/%Y")
        if phone_val:
            out["babyFormPhone"] = phone_val
        if address:
            out["babyFormAddress"] = address
        if guardian:
            out["babyFormGuardian"] = guardian
        if bg_val:
            out["babyFormBlood"] = bg_val
    elif form_id == "maternalProfileForm":
        if name:
            out["motherFormName"] = name
        if age_val is not None and 12 <= age_val <= 60:
            out["motherFormAge"] = age_val
        if phone_val:
            out["motherFormPhone"] = phone_val
        if address:
            out["motherFormAddress"] = address
        if indic_d:
            if any(k in text for k in ("ಋತು", "LMP", "lmp", "ಕೊನೆಯ")):
                out["motherFormDueDate"] = (indic_d + timedelta(days=280)).strftime("%d %b %Y")
            else:
                out["motherFormDueDate"] = indic_d.strftime("%d %b %Y")
        if weight_val is not None and 25 <= weight_val <= 150:
            out["motherFormWeight"] = f"{weight_val:g} kg"
        if iron_val:
            out["motherFormIron"] = iron_val
        if bg_val:
            out["motherFormBlood"] = bg_val

    return out
