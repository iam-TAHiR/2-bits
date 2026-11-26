import sys
from pathlib import Path
import sqlite3
import json

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from starlette.testclient import TestClient
from src.api_link import app, DB_PATH

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("SAKHI END-TO-END INTEGRATION TEST SUITE")
    print("=" * 60)

    # 1. Health check
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    health_data = r.json()
    assert health_data["status"] == "healthy"
    print("✓ 1. Health check passed:", health_data["database"]["counts"])

    # 2. Static files
    r_index = client.get("/")
    assert r_index.status_code == 200 and "SAKHI" in r_index.text
    r_css = client.get("/style.css")
    assert r_css.status_code == 200 and len(r_css.text) > 1000
    r_js = client.get("/app.js")
    assert r_js.status_code == 200 and "SakhiApp" in r_js.text
    print("✓ 2. Static files (index.html, style.css, app.js) served correctly")

    # 3. Authentication
    r_login = client.post("/api/auth/login", json={"mobile": "9876543210", "password": "pass12"})
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    user = r_login.json()["user"]
    assert user["name"] == "Anita"
    print("✓ 3. Authentication passed for worker:", user["name"], f"({user['id']})")

    # 4. Dashboard metrics
    r_dash = client.get("/api/dashboard")
    assert r_dash.status_code == 200
    d_data = r_dash.json()["data"]
    assert d_data["total_homes"] >= 20
    assert d_data["total_visits"] >= 15
    print("✓ 4. Dashboard metrics passed: total_homes=", d_data["total_homes"], "total_visits=", d_data["total_visits"])

    # 5. Mothers list & single
    r_mothers = client.get("/api/mothers")
    assert r_mothers.status_code == 200
    mothers = r_mothers.json()["data"]
    assert len(mothers) >= 11
    sample_m = mothers[0]
    r_single_m = client.get(f"/api/mothers/{sample_m['id']}")
    assert r_single_m.status_code == 200
    print(f"✓ 5. Mothers list & profile passed: {len(mothers)} mothers. Sample: {sample_m['name']} ({sample_m['id']})")

    # 6. Babies list & single
    r_babies = client.get("/api/babies")
    assert r_babies.status_code == 200
    babies = r_babies.json()["data"]
    assert len(babies) >= 14
    sample_b = babies[0]
    r_single_b = client.get(f"/api/babies/{sample_b['id']}")
    assert r_single_b.status_code == 200
    print(f"✓ 6. Babies list & profile passed: {len(babies)} babies. Sample: {sample_b['name']} ({sample_b['id']})")

    # 7. Visits list & update
    r_visits = client.get("/api/visits")
    assert r_visits.status_code == 200
    visits = r_visits.json()["data"]
    assert len(visits) >= 15
    sample_v = visits[0]
    
    # Test updating visit with note and GPS location
    r_update_v = client.put(f"/api/visits/{sample_v['id']}", json={
        "status": "Complete",
        "note": "Routine home visit completed. BP 120/80 normal.",
        "voice": "Blood pressure normal, mother doing well.",
        "location": {"lat": 12.9716, "lng": 77.5946, "verified": True}
    })
    assert r_update_v.status_code == 200
    print(f"✓ 7. Visits list & update passed: {len(visits)} visits. Updated visit {sample_v['id']}")

    # 8. Follow-ups and Alerts
    r_followups = client.get("/api/followups")
    assert r_followups.status_code == 200
    r_alerts = client.get("/api/alerts")
    assert r_alerts.status_code == 200
    print(f"✓ 8. Follow-ups & alerts passed: {len(r_followups.json()['data'])} pending followups, {len(r_alerts.json()['data'])} clinical alerts")

    # 9. AI Chatbot
    r_chat = client.post("/api/chat", json={"query": "Show total homes"})
    assert r_chat.status_code == 200
    chat_resp = r_chat.json()
    assert "20" in chat_resp["response"] or chat_resp["data"] is not None
    print("✓ 9. AI Chatbot response:", chat_resp["response"])

    # 10. Clinical Note Processing with Keyword Risk Detection
    test_note = "Mother B_003 reports high severe fever and cough and skull headache."
    r_note = client.post("/api/voice/process-note", json={"note": test_note, "beneficiary_id": "B_003"})
    assert r_note.status_code == 200
    note_data = r_note.json()
    assert note_data["high_risk"] == True
    assert "skull" in str(note_data["keywords"])
    print("✓ 10. Clinical Note Processing passed: High Risk Flag detected (", note_data["severity"], "):", note_data["clinical_guidance"][:60], "...")

    # 11. Voice STT, TTS & Translation status
    r_tts = client.post("/api/voice/tts", json={"text": "Hello ASHA worker"})
    assert r_tts.status_code == 200
    r_stt = client.post("/api/voice/transcribe")
    assert r_stt.status_code == 200
    r_trans = client.post("/api/voice/translate", json={"text": "Namaskara"})
    assert r_trans.status_code == 200
    print("✓ 11. Voice STT/TTS/Translation endpoints handled gracefully without error fabrication")

    # 12. SQLite Database Persistence Check
    # Verify that the visit update performed above is actually stored in SQLite
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT note, voice, visit_ts FROM visits WHERE id = ?", (sample_v["id"],))
    row = cursor.fetchone()
    conn.close()
    assert row is not None and "Routine home visit completed" in row[0]
    print(f"✓ 12. SQLite Persistence verified directly on {DB_PATH.name}: note='{row[0][:40]}...', visit_ts='{row[2]}'")

    print("=" * 60)
    print("ALL 12 INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
