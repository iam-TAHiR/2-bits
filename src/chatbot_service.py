"""SAKHI — Grounded AI Chatbot & Controlled Workflow Assistant Service.

Combines:
1. Approved NHM / IMNCI / ASHA protocol knowledge retrieval (with source citations).
2. Live SQLite & deterministic prioritization engine queries (zero fabrication).
3. Controlled workflow action proposals (via voice_service + voice_action_service).
4. Immediate danger-sign escalation guidance without autonomous diagnosis.
"""

import sqlite3
from typing import Any, Dict, List, Optional

try:
    from src.prioritization import compute_all_priorities
    from src.voice_service import detect_emergency_indicators, parse_voice_transcript
    from src.voice_action_service import prepare_action_preview
    from src.multilingual_nlp import detect_script_language
    from src.sarvam_service import SarvamSpeechService
except ImportError:
    from prioritization import compute_all_priorities
    from voice_service import detect_emergency_indicators, parse_voice_transcript
    from voice_action_service import prepare_action_preview
    from multilingual_nlp import detect_script_language
    from sarvam_service import SarvamSpeechService

_sarvam_chat_svc = SarvamSpeechService()


APPROVED_PROTOCOL_KB = [
    {
        "id": "NHM_ANC_ROUTINE",
        "keywords": ["routine antenatal", "anc visit", "check during", "antenatal check", "pregnant check"],
        "source": "NHM ASHA Module / Maternal Health Guidelines",
        "guidance": (
            "During a routine ANC home visit, verify MCP card entries, ask about IFA and Calcium tablet intake, "
            "check for danger signs (vaginal bleeding, severe headache, blurred vision, convulsions, high fever), "
            "and remind the mother of her next ANM/PHC checkup and TT/Td immunization."
        ),
    },
    {
        "id": "NHM_IFA_IRON",
        "keywords": ["iron", "ifa", "anemia", "folic acid"],
        "source": "NHM Anemia Mukt Bharat / ASHA Handbook",
        "guidance": (
            "IFA (Iron-Folic Acid) tablets help prevent maternal anemia and are recommended daily after food "
            "(starting from the 2nd trimester per ANC schedule). If the mother missed doses or reports dizziness, "
            "weakness, or nausea, counsel her to resume regular intake and consult the ANM or PHC Medical Officer."
        ),
    },
    {
        "id": "NHM_CALCIUM_GAP",
        "keywords": ["calcium", "gap between"],
        "source": "NHM Maternal Nutrition Guidelines",
        "guidance": (
            "Calcium supplementation during pregnancy should not be taken at the same time as Iron (IFA) tablets "
            "because calcium reduces iron absorption. Advise at least a 2-hour gap between Calcium and IFA tablets."
        ),
    },
    {
        "id": "UIP_IMMUNIZATION",
        "keywords": ["vaccine", "vaccination", "immunization", "pentavalent", "bcg", "measles", "opv", "mr-1"],
        "source": "Universal Immunization Programme (UIP) Schedule",
        "guidance": (
            "Per UIP schedule: Birth doses (BCG, OPV-0, Hep-B), 6/10/14 weeks (bOPV, Pentavalent, Rotavirus, fIPV/PCV), "
            "and 9 months (MR-1, Vitamin A 1st dose). Always verify the child's MCP card before marking doses."
        ),
    },
    {
        "id": "NHM_MATERNAL_CARE",
        "keywords": ["maternal care", "maternal health", "pregnancy care", "anc care"],
        "source": "NHM Maternal Health & ASHA Handbook",
        "guidance": (
            "Maternal care in ASHA workflow includes at least 4 ANC checkups, regular IFA and Calcium supplementation "
            "(2 hours apart), TT/Td vaccination, monitoring weight and danger signs (bleeding, severe headache, "
            "blurred vision, convulsions, high fever), and birth preparedness. This is workflow guidance, not a medical diagnosis."
        ),
    },
    {
        "id": "DOCUMENT_VISIT",
        "keywords": ["document this visit", "how should i document", "what does this field mean", "mcp card"],
        "source": "SAKHI Field Register Workflow Guide",
        "guidance": (
            "To document a visit: record the beneficiary ID, visit type (ANC/PNC/Vaccination/General), observations "
            "in plain words, any danger-sign flag if present, and schedule the next follow-up date. Always review and confirm before saving."
        ),
    },
]


def _retrieve_protocol_guidance(query: str) -> Optional[Dict[str, str]]:
    low = (query or "").lower()
    for item in APPROVED_PROTOCOL_KB:
        if any(kw in low for kw in item["keywords"]):
            return item
    return None


def _finalize_multilingual_response(res: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
    """Translate response to Kannada/Hindi via Sarvam Translate when configured."""
    if target_lang in ("kn-IN", "hi-IN") and res.get("response") and _sarvam_chat_svc.is_configured():
        t_res = _sarvam_chat_svc.translate_text(
            res["response"],
            source_language_code="en-IN",
            target_language_code=target_lang,
        )
        if t_res.get("success") and t_res.get("translated_text"):
            res["response_en"] = res["response"]
            res["response"] = t_res["translated_text"]
            res["tts_text"] = t_res["translated_text"]
            res["language_code"] = target_lang
            return res
    res["language_code"] = target_lang
    return res


def handle_chat_message(
    query: str,
    conn: sqlite3.Connection,
    backend_module: Any = None,
    beneficiary_id: Optional[str] = None,
    current_draft: Optional[Dict[str, Any]] = None,
    screen_context: Optional[Dict[str, Any]] = None,
    shared_tab_context: Optional[Dict[str, Any]] = None,
    language_code: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Handle multilingual information queries, page-aware questions, and controlled workflow actions."""
    raw_q = (query or "").strip()
    detected_lang = detect_script_language(raw_q, hint=language_code)

    # Translate Indic query to English for unified grounding (fallback to native keywords if offline)
    translated_q = raw_q
    if detected_lang in ("kn-IN", "hi-IN") and _sarvam_chat_svc.is_configured():
        t_in = _sarvam_chat_svc.translate_text(raw_q, source_language_code=detected_lang, target_language_code="en-IN")
        if t_in.get("success") and t_in.get("translated_text"):
            translated_q = t_in["translated_text"]

    q = translated_q
    low = q.lower()
    raw_low = raw_q.lower()

    # 1. Immediate danger-sign check (never delay emergency instructions)
    emergency = detect_emergency_indicators(q) or detect_emergency_indicators(raw_q)
    if emergency:
        return _finalize_multilingual_response({
            "success": True,
            "intent": "emergency_escalation",
            "response": (
                f"⚠️ {emergency['warning']}\n"
                f"Detected indicator(s): {', '.join(emergency['matched_indicators'])}.\n"
                f"{emergency['instruction']}"
            ),
            "emergency_alert": emergency,
            "source": "NHM Danger-Sign Escalation Protocol",
            "tts_text": f"Urgent alert. {emergency['instruction']}",
        }, detected_lang)

    # 2. Load live prioritization & SQLite data
    prio_result = compute_all_priorities(conn)
    households = prio_result["households"]
    summary = prio_result["summary"]

    # 2a. Explicit Shared-Tab / Screen Context Questions
    is_screen_q = any(p in low for p in (
        "what i'm seeing", "what am i seeing", "seeing here", "this screen",
        "this dashboard", "summarize this register", "this beneficiary",
        "information is missing", "missing from this"
    ))
    if is_screen_q:
        ctx = screen_context or {}
        tab = shared_tab_context or {}
        tab_active = bool(tab.get("sharing_active"))
        active_screen = tab.get("active_screen") or ctx.get("active_screen") or "home"
        sel_ben = tab.get("selected_beneficiary_id") or ctx.get("selected_beneficiary_id") or beneficiary_id
        visible_summary = tab.get("visible_text_summary") or ctx.get("visible_text_summary") or ""

        if ("why" in low or "due" in low or "visit" in low or "this beneficiary" in low) and "missing" not in low and sel_ben:
            target = next((h for h in households if h["beneficiary_id"].lower() == sel_ben.lower()), None)
            if target:
                msg = (
                    f"{target['name']} ({target['beneficiary_id']}) is {target['priority_code']} ({target['priority_label']}).\n"
                    f"Reason: {'; '.join(target['reasons'])}\n"
                    f"Pending Visits: {target['pending_visits_count']} | Next Follow-up Date: {target['followup_date'] or 'Not scheduled'}\n"
                    f"Next action: {target['suggested_action']}"
                )
                return _finalize_multilingual_response({
                    "success": True,
                    "intent": "screen_context_explanation",
                    "response": msg,
                    "data": target,
                    "source": "SAKHI Shared Tab + Prioritization Engine" if tab_active else "SAKHI Screen Context + Prioritization Engine",
                }, detected_lang)

        if "missing" in low:
            missing_list = [h for h in households if h["has_missing_data"]]
            if sel_ben:
                target = next((h for h in households if h["beneficiary_id"].lower() == sel_ben.lower()), None)
                if target:
                    msg = target["verification_warning"] or f"No missing fields flagged for {target['name']} ({sel_ben})."
                    return _finalize_multilingual_response({
                        "success": True,
                        "intent": "screen_missing_info",
                        "response": msg,
                        "data": target,
                        "source": "SAKHI Data Verification Check",
                    }, detected_lang)
            msg = (
                f"{len(missing_list)} household(s) have missing fields needing verification:\n"
                + "\n".join(f"• {h['beneficiary_id']} ({h['name']}): {', '.join(h['missing_data_items'])}" for h in missing_list[:5])
            )
            return _finalize_multilingual_response({
                "success": True,
                "intent": "screen_missing_info",
                "response": msg,
                "data": missing_list[:5],
                "source": "SAKHI Data Verification Check",
            }, detected_lang)

        if tab_active:
            msg = (
                f"Shared Tab Active ({active_screen}):\n"
                f"Live Priority Summary: {summary['total_households']} households — "
                f"{summary['immediate_escalation']} RED, {summary['high_priority']} High Priority, "
                f"{summary['overdue']} Overdue, {summary['due_today']} Due Today, {summary['upcoming']} Upcoming, "
                f"{summary['missing_data']} needing verification."
                + (f"\nVisible context: {visible_summary[:240]}" if visible_summary else "")
            )
            return _finalize_multilingual_response({
                "success": True,
                "intent": "shared_tab_summary",
                "response": msg,
                "data": summary,
                "source": "Shared Browser Tab + SAKHI Live SQLite",
            }, detected_lang)

        # Not actively sharing tab via getDisplayMedia
        msg = (
            f"You are viewing SAKHI ({active_screen}). Live register summary: {summary['total_households']} households "
            f"({summary['high_priority']} High Priority, {summary['overdue']} Overdue, {summary['upcoming']} Upcoming, "
            f"{summary['missing_data']} needing verification). "
            "Tip: Click 'Share Current Tab' if you want to grant permission to share your active browser tab."
        )
        return _finalize_multilingual_response({
            "success": True,
            "intent": "dashboard_summary",
            "response": msg,
            "data": summary,
            "source": "SAKHI Live SQLite (Tab sharing not enabled)",
        }, detected_lang)

    # 2b. Multilingual & English Priority / Household / Vaccination / Follow-up Queries
    kn_attention = any(k in raw_q for k in ("ಭೇಟಿ ಕೊಡಬೇಕು", "ಯಾವ ಮನೆ", "ಬಾಕಿ ಕೆಲಸ", "ಬಾಕಿ"))
    kn_why = "ಏಕೆ ಆದ್ಯತೆ" in raw_q or "ಆದ್ಯತೆ ಕೊಟ್ಟಿದ್ದೀರಿ" in raw_q
    kn_vaccine = "ಲಸಿಕೆ" in raw_q
    hi_attention = any(k in raw_q for k in ("किन घरों", "ध्यान", "बकाया", "बाकी"))
    hi_vaccine = "टीका" in raw_q

    if kn_attention or kn_why or kn_vaccine or hi_attention or hi_vaccine or any(p in low for p in (
        "need attention", "overdue", "due today", "priority", "prioritized", "complete today",
        "why is", "why was", "pregnant women", "vaccination", "upcoming",
        "not been visited", "next five", "next 5", "next tasks", "follow-up", "follow up", "pending"
    )):
        if "why" in low or kn_why or "next tasks" in low or (beneficiary_id and "flagged" in low):
            target = None
            if beneficiary_id:
                target = next((h for h in households if h["beneficiary_id"].lower() == beneficiary_id.lower()), None)
            if not target:
                for h in households:
                    if h["beneficiary_id"].lower() in low or (h["name"] and h["name"].lower().split()[0] in low):
                        target = h
                        break
            if not target and kn_why:
                target = households[0] if households else None
            if target:
                reasons_txt = "; ".join(target["reasons"])
                missing_txt = f"\nVerification note: {target['verification_warning']}" if target["has_missing_data"] else ""
                msg = (
                    f"{target['name']} ({target['beneficiary_id']}) is {target['priority_code']} ({target['priority_label']}).\n"
                    f"Reason: {reasons_txt}\n"
                    f"Next action: {target['suggested_action']}{missing_txt}"
                )
                return _finalize_multilingual_response({
                    "success": True,
                    "intent": "priority_explanation",
                    "response": msg,
                    "data": target,
                    "source": "SAKHI Deterministic Prioritization Engine",
                    "tts_text": f"{target['name']} is {target['priority_label']}. {target['primary_reason']}",
                }, detected_lang)

        if "vaccin" in low or kn_vaccine or hi_vaccine:
            vac_due = [h for h in households if any("vaccin" in r.lower() for r in h["reasons"])]
            lines = [f"• {h['beneficiary_id']} ({h['name']}): {h['primary_reason']}" for h in vac_due[:6]]
            msg = (
                f"{len(vac_due)} household(s) have vaccination follow-ups due/upcoming:\n" + "\n".join(lines)
                if vac_due else "No households currently have pending vaccination follow-ups."
            )
            return _finalize_multilingual_response({
                "success": True,
                "intent": "priority_vaccine_due",
                "response": msg,
                "data": vac_due,
                "source": "SAKHI SQLite + Prioritization Engine",
            }, detected_lang)

        if "pregnant" in low:
            preg_list = [h for h in households if "mother" in h["beneficiary_type"].lower() or h["home_status"] == "PREGNANT"]
            pending = [h for h in preg_list if h["pending_visits_count"] > 0 or h["status_bucket"] in ("high_priority", "overdue", "due_today", "upcoming")]
            lines = [f"• {h['beneficiary_id']} ({h['name']}): {h['primary_reason']}" for h in pending[:6]]
            msg = (
                f"{len(pending)} pregnant mother household(s) have active/upcoming follow-ups:\n" + "\n".join(lines)
                if pending else "No pregnant mother households have pending follow-ups."
            )
            return _finalize_multilingual_response({
                "success": True,
                "intent": "priority_pregnant_pending",
                "response": msg,
                "data": pending,
                "source": "SAKHI SQLite + Prioritization Engine",
            }, detected_lang)

        if "overdue" in low:
            overdue_list = [h for h in households if h["status_bucket"] == "overdue"]
            if not overdue_list:
                msg = "0 households currently have overdue follow-ups."
            else:
                lines = [f"• {h['beneficiary_id']} ({h['name']}): {h['primary_reason']}" for h in overdue_list[:6]]
                msg = f"{len(overdue_list)} household(s) have overdue follow-ups:\n" + "\n".join(lines)
            return _finalize_multilingual_response({
                "success": True,
                "intent": "priority_overdue",
                "response": msg,
                "data": overdue_list,
                "source": "SAKHI SQLite + Prioritization Engine",
                "tts_text": f"{len(overdue_list)} households have overdue follow-ups.",
            }, detected_lang)

        if "due today" in low or "need attention today" in low or "complete today" in low or kn_attention or hi_attention:
            urgent_or_due = [
                h for h in households
                if h["status_bucket"] in ("immediate_escalation", "high_priority", "due_today", "overdue")
            ]
            if not urgent_or_due:
                msg = "No households are flagged as urgent, overdue, or due today."
            else:
                lines = [f"• {h['beneficiary_id']} ({h['name']}) [{h['priority_code']}]: {h['primary_reason']}" for h in urgent_or_due[:6]]
                msg = f"{len(urgent_or_due)} household(s) need attention first:\n" + "\n".join(lines)
            return _finalize_multilingual_response({
                "success": True,
                "intent": "priority_attention_today",
                "response": msg,
                "data": urgent_or_due[:6],
                "source": "SAKHI SQLite + Prioritization Engine",
                "tts_text": f"{len(urgent_or_due)} households need attention.",
            }, detected_lang)

        # General next 5 priority households
        top5 = households[:5]
        lines = [f"{i+1}. {h['beneficiary_id']} ({h['name']}) [{h['priority_code']} · {h['priority_label']}]: {h['primary_reason']}" for i, h in enumerate(top5)]
        msg = (
            f"Summary ({summary['total_households']} households: {summary['immediate_escalation']} RED, "
            f"{summary['high_priority']} High, {summary['overdue']} Overdue, {summary['due_today']} Due Today):\n"
            + "\n".join(lines)
        )
        return _finalize_multilingual_response({
            "success": True,
            "intent": "priority_top5",
            "response": msg,
            "data": top5,
            "source": "SAKHI SQLite + Prioritization Engine",
            "tts_text": f"Top priority is {top5[0]['name']} because {top5[0]['primary_reason']}" if top5 else msg,
        }, detected_lang)

    # 2c. Conversational SAKHI / Alerts / Beneficiary / Pending Tasks / Dashboard Summaries
    active_screen = (screen_context or {}).get("active_screen") or "home"
    sel_ben_id = beneficiary_id or (screen_context or {}).get("selected_beneficiary_id")

    # What is SAKHI / Help / Purpose / How to register
    if any(p in low for p in (
        "what is sakhi", "purpose of this", "what can you help", "help me with",
        "how do i use", "what features", "how do i register", "how to register",
        "how does prioritization", "about sakhi"
    )):
        if "register" in low:
            msg = (
                "To register a beneficiary:\n"
                "• Pregnant Mother: Open Maternal Health → Add New Mother (or tap Voice and speak details like name, age, address, weight, blood group).\n"
                "• Child: Open Vaccine Tracker → Add New Baby (or use Voice to fill name, DOB, gender, address, guardian).\n"
                "SAKHI will populate the form, highlight missing fields, and save to SQLite only after you confirm."
            )
        else:
            msg = (
                f"SAKHI is your ASHA workflow and household prioritization assistant. Currently managing {summary['total_households']} households "
                f"({summary['high_priority']} High Priority, {summary['overdue']} Overdue, {summary['upcoming']} Upcoming, {summary['missing_data']} needing verification).\n\n"
                "I can help you:\n"
                "• Identify which households need visits first and explain why\n"
                "• Explain clinical alerts and follow-up tasks\n"
                "• Look up maternal, child, and vaccination records\n"
                "• Fill registration or visit forms by voice (Kannada, Hindi, or English)"
            )
        return _finalize_multilingual_response({
            "success": True,
            "intent": "sakhi_overview",
            "response": msg,
            "source": "SAKHI Workflow Assistant",
            "tts_text": msg,
        }, detected_lang)

    # Alerts explanation ("Explain my alerts", "What does this alert mean?", "Explain alerts on this page")
    if "alert" in low or ("flagged" in low and not sel_ben_id):
        flagged_visits = conn.execute(
            """
            SELECT v.id, v.beneficiary_id, v.flag, v.note, v.due_date, v.type,
                   COALESCE(p.mother_name, c.child_name, v.beneficiary_id) AS person_name
            FROM visits v
            LEFT JOIN pregnancies p ON v.beneficiary_id = p.beneficiary_id
            LEFT JOIN children c ON v.beneficiary_id = c.beneficiary_id
            WHERE v.flag IN ('S', 'HS', 'H', 'HM', 'M')
            ORDER BY CASE v.flag WHEN 'S' THEN 0 WHEN 'HS' THEN 1 WHEN 'H' THEN 2 WHEN 'HM' THEN 3 ELSE 4 END, v.due_date ASC
            """
        ).fetchall()
        flag_desc = {
            "S": "Severe / Emergency — Immediate referral to PHC/FRU required",
            "HS": "High-Severe — Urgent medical care needed today",
            "H": "High Risk — Visit PHC or Sub-Centre today",
            "HM": "High-Moderate — See ANM/Doctor by tomorrow",
            "M": "Moderate — Supportive home care and monitoring",
        }
        if not flagged_visits:
            msg = "There are currently 0 flagged clinical alerts in the register."
        else:
            lines = [
                f"• {r['person_name']} ({r['beneficiary_id']}, Visit {r['id']}): Flag {r['flag']} ({flag_desc.get(r['flag'], r['flag'])})"
                + (f" — {r['note']}" if r['note'] else "")
                for r in flagged_visits[:6]
            ]
            msg = f"You have {len(flagged_visits)} flagged clinical alert(s):\n" + "\n".join(lines)
        return _finalize_multilingual_response({
            "success": True,
            "intent": "alerts_explanation",
            "response": msg,
            "data": [dict(r) for r in flagged_visits[:6]],
            "source": "SAKHI Alerts & Keyword4 Protocol",
            "tts_text": f"You have {len(flagged_visits)} flagged clinical alerts.",
        }, detected_lang)

    # Pending tasks / visits / "What should I do next?" / "Summarize my dashboard"
    if any(p in low for p in (
        "pending task", "my tasks", "what should i do next", "who should i visit",
        "summarize my dashboard", "dashboard summary", "visits are pending", "how many visits"
    )):
        pending_cnt = conn.execute("SELECT count(*) FROM visits WHERE visit_ts IS NULL OR visit_ts = ''").fetchone()[0]
        total_visits_cnt = conn.execute("SELECT count(*) FROM visits").fetchone()[0]
        top3 = households[:3]
        lines = [f"{i+1}. {h['beneficiary_id']} ({h['name']}) [{h['priority_code']}]: {h['primary_reason']} → {h['suggested_action']}" for i, h in enumerate(top3)]
        msg = (
            f"Dashboard Summary: {summary['total_households']} households assigned, {pending_cnt} of {total_visits_cnt} visits pending "
            f"({summary['immediate_escalation']} RED, {summary['high_priority']} High Priority, {summary['overdue']} Overdue, {summary['due_today']} Due Today, {summary['upcoming']} Upcoming).\n\n"
            f"Next recommended actions:\n" + "\n".join(lines)
        )
        return _finalize_multilingual_response({
            "success": True,
            "intent": "dashboard_tasks_summary",
            "response": msg,
            "data": summary,
            "source": "SAKHI Live SQLite + Prioritization Engine",
            "tts_text": f"You have {pending_cnt} pending visits across {summary['total_households']} households.",
        }, detected_lang)

    # Beneficiary register overview or selected beneficiary ("Tell me about the beneficiaries in my register", "beneficiary I am viewing", "due for another visit")
    if any(p in low for p in ("beneficiar", "i am viewing", "due for another visit", "this mother", "this child")):
        if sel_ben_id:
            target = next((h for h in households if h["beneficiary_id"].lower() == sel_ben_id.lower()), None)
            if target:
                msg = (
                    f"Selected Beneficiary: {target['name']} ({target['beneficiary_id']})\n"
                    f"• Type: {target['beneficiary_type']} | Area: {target['address']}\n"
                    f"• Priority: {target['priority_code']} ({target['priority_label']})\n"
                    f"• Reason: {'; '.join(target['reasons'])}\n"
                    f"• Pending Visits: {target['pending_visits_count']} | Follow-up Date: {target['followup_date'] or 'Not scheduled'}\n"
                    f"• Next Action: {target['suggested_action']}"
                )
                return _finalize_multilingual_response({
                    "success": True,
                    "intent": "selected_beneficiary_detail",
                    "response": msg,
                    "data": target,
                    "source": "SAKHI Selected Beneficiary Record",
                    "tts_text": f"{target['name']} is {target['priority_label']}. {target['primary_reason']}",
                }, detected_lang)
        preg_cnt = conn.execute("SELECT count(*) FROM pregnancies").fetchone()[0]
        child_cnt = conn.execute("SELECT count(*) FROM children").fetchone()[0]
        msg = (
            f"Your register currently has {summary['total_households']} households: {preg_cnt} maternal/pregnancy records "
            f"and {child_cnt} child records. Top priority households: "
            + ", ".join(f"{h['name']} ({h['beneficiary_id']}, {h['priority_code']})" for h in households[:4])
            + "."
        )
        return _finalize_multilingual_response({
            "success": True,
            "intent": "beneficiary_register_summary",
            "response": msg,
            "data": {"households": summary["total_households"], "pregnancies": preg_cnt, "children": child_cnt},
            "source": "SAKHI SQLite Register",
        }, detected_lang)

    # 3. Check if query is a Controlled Workflow Action request
    parsed = parse_voice_transcript(q, current_draft=current_draft, beneficiary_id=beneficiary_id)
    if parsed.get("intent") in (
        "register_mother", "register_child", "correct_draft",
        "record_visit", "schedule_followup", "complete_followup",
        "reschedule_followup", "cancel_followup",
    ):
        preview = prepare_action_preview(parsed, conn)
        if preview.get("needs_clarification"):
            return {
                "success": True,
                "intent": "clarification_needed",
                "response": preview["clarification"],
                "action_preview": preview,
            }
        return {
            "success": True,
            "intent": parsed["intent"],
            "response": f"{preview.get('preview_title', 'Action ready')}. Please review and confirm before saving.",
            "action_preview": preview,
            "tts_text": "Action preview is ready for your confirmation.",
        }

    # 4. Approved Protocol Knowledge Retrieval
    kb = _retrieve_protocol_guidance(q)
    if kb:
        return {
            "success": True,
            "intent": "protocol_guidance",
            "response": f"{kb['guidance']}\n\nSource: {kb['source']} (Workflow guidance only — not a medical diagnosis).",
            "source": kb["source"],
            "tts_text": kb["guidance"],
        }

    # 5. Existing backend metric/intent handler (only if it actually matched a known metric, NOT its unknown fallback!)
    if backend_module is not None:
        try:
            bot_res = backend_module.handle_asha_query(q)
            msg = bot_res.get("message") or ""
            data = bot_res.get("data")
            intent = bot_res.get("intent")
            is_unknown = (intent in (None, "unknown", "fallback")) or ("could not identify your request" in msg.lower())
            if not is_unknown:
                if not msg:
                    if isinstance(data, dict):
                        msg = "\n".join(f"• {k.replace('_', ' ').title()}: {v}" for k, v in data.items())
                    elif isinstance(data, (int, float, str)):
                        msg = f"The current count is {data}."
                if msg:
                    return _finalize_multilingual_response({
                        "success": True,
                        "intent": intent,
                        "response": msg,
                        "data": data,
                        "source": "SAKHI SQLite Metrics",
                    }, detected_lang)
        except Exception:
            pass

    # 6. Grounded Conversational AI (Sarvam-105B with retrieved page + DB context, or honest offline summary)
    context_snapshot = (
        f"Active Page: {active_screen}. "
        f"Households: {summary['total_households']} total, {summary['immediate_escalation']} RED, "
        f"{summary['high_priority']} High Priority, {summary['overdue']} Overdue, "
        f"{summary['due_today']} Due Today, {summary['upcoming']} Upcoming, {summary['missing_data']} Missing Data. "
        f"Top 3 priorities: "
        + "; ".join(f"{h['beneficiary_id']} {h['name']} ({h['priority_code']}): {h['primary_reason']}" for h in households[:3])
    )
    if _sarvam_chat_svc.is_configured():
        msgs = [
            {
                "role": "system",
                "content": (
                    "You are SAKHI, a helpful, concise ASHA healthcare workflow assistant. "
                    "Use ONLY the provided live register context for counts/beneficiaries. "
                    "Never invent patient records or diagnose medical conditions. "
                    f"Context: {context_snapshot}"
                ),
            }
        ]
        for turn in (conversation_history or [])[-4:]:
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                msgs.append({"role": turn["role"], "content": str(turn["content"])[:500]})
        msgs.append({"role": "user", "content": q})

        llm_res = _sarvam_chat_svc.chat_completion(msgs)
        if llm_res.get("success") and llm_res.get("content"):
            return _finalize_multilingual_response({
                "success": True,
                "intent": "contextual_ai_response",
                "response": llm_res["content"],
                "source": f"SAKHI Context + Sarvam AI ({llm_res.get('model', 'sarvam-105b')})",
                "tts_text": llm_res["content"],
            }, detected_lang)

    # Graceful, helpful grounded response when LLM is offline/unavailable (never "I could not identify your request")
    fallback_msg = (
        f"Here is your live SAKHI context ({active_screen}): {summary['total_households']} households "
        f"({summary['high_priority']} High Priority, {summary['overdue']} Overdue, {summary['upcoming']} Upcoming). "
        f"Top household needing attention: {households[0]['name']} ({households[0]['beneficiary_id']}) — {households[0]['primary_reason']}.\n"
        "You can ask me about your alerts, pending visits, why a household is prioritized, maternal/child care guidelines, or how to register a beneficiary."
        if households else
        "I am SAKHI, your ASHA workflow assistant. Ask me about households, alerts, pending visits, or maternal/child care."
    )
    return _finalize_multilingual_response({
        "success": True,
        "intent": "contextual_summary_fallback",
        "response": fallback_msg,
        "source": "SAKHI Live SQLite Context",
        "tts_text": fallback_msg,
    }, detected_lang)
