# api.py - Flask REST API wrapping the scheduler Python logic
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import OrderedDict
import datetime
import os

from config import (SPORTS, INJURY_TASKS, SEVERITIES, PHYSIOS,
                     SEVERE_DOCTOR, CASE_OVERRIDES, SEVERITY_RULES, SPORT_RULES)
from audit import AUDIT_LOG
from store import (registry, followups, history, generate_demo_data,
                   new_case_id)
from scheduler import (schedule_followup, get_upcoming, get_missed,
                       mark_done, auto_reschedule, todays_queue, stats)

app = Flask(__name__)
CORS(app)

# ── Helpers ──────────────────────────────────────────────

def fmt(d):
    return d.strftime("%a %d-%b-%Y")

def followup_to_dict(f):
    case = registry.get(f.case_id, {})
    return {
        "fid": f.fid,
        "case_id": f.case_id,
        "name": case.get("name", "?"),
        "sport": case.get("sport", "?"),
        "injury": case.get("injury", "?"),
        "severity": case.get("severity", "?"),
        "due": fmt(f.due),
        "due_iso": f.due.isoformat(),
        "physio": f.physio,
        "status": f.status,
        "tasks": sorted(f.tasks),
    }

def case_to_dict(cid, case):
    return {
        "case_id": cid,
        "name": case["name"],
        "age": case["age"],
        "sport": case["sport"],
        "injury": case["injury"],
        "severity": case["severity"],
        "physio": case["physio"],
    }

# ── Init demo data ───────────────────────────────────────

generate_demo_data()

# ── Routes ───────────────────────────────────────────────

@app.route("/api/config", methods=["GET"])
def get_config():
    """Return dropdowns / options for forms."""
    return jsonify({
        "sports": SPORTS,
        "injuries": list(INJURY_TASKS.keys()),
        "severities": SEVERITIES,
        "physios": PHYSIOS,
    })


@app.route("/api/cases", methods=["GET"])
def get_cases():
    """List all cases."""
    cases = [case_to_dict(cid, case) for cid, case in registry.items()]
    return jsonify(cases)


@app.route("/api/cases", methods=["POST"])
def add_case():
    """Add a new case."""
    data = request.json
    cid = new_case_id()
    try:
        severity = data["severity"]
        physio = SEVERE_DOCTOR if severity == "severe" else data["physio"]
        registry[cid] = {
            "name": data["name"],
            "age": int(data["age"]),
            "sport": data["sport"],
            "injury": data["injury"],
            "severity": severity,
            "physio": physio,
        }
        history[cid] = OrderedDict()
        history[cid][0] = f"Case created for {data['name']}"
        return jsonify({"ok": True, "case_id": cid, "message": f"Created case {cid}"}), 201
    except (ValueError, KeyError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/followups/upcoming", methods=["GET"])
def api_upcoming():
    return jsonify([followup_to_dict(f) for f in get_upcoming()])


@app.route("/api/followups/missed", methods=["GET"])
def api_missed():
    return jsonify([followup_to_dict(f) for f in get_missed()])


@app.route("/api/followups/today", methods=["GET"])
def api_today():
    q = todays_queue()
    return jsonify([followup_to_dict(f) for f in q])


@app.route("/api/followups/all", methods=["GET"])
def api_all_followups():
    return jsonify([followup_to_dict(f) for f in followups])


@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    data = request.json
    cid = data.get("case_id", "").strip().upper()
    result = schedule_followup(cid)
    if result is None:
        return jsonify({"ok": False, "error": f"Case {cid} not found"}), 404
    fu, explanation = result
    if fu is not None:
        return jsonify({
            "ok": True,
            "followup": followup_to_dict(fu),
            "explanation": explanation,
        })
    return jsonify({"ok": False, "error": explanation}), 400


@app.route("/api/mark-done", methods=["POST"])
def api_mark_done():
    data = request.json
    fid = data.get("fid", "").strip().upper()
    result = mark_done(fid)
    return jsonify({"ok": True, "message": result})


@app.route("/api/auto-reschedule", methods=["POST"])
def api_auto_reschedule():
    explanations = auto_reschedule()
    return jsonify({
        "ok": True,
        "count": len(explanations),
        "explanations": explanations,
    })


@app.route("/api/override", methods=["POST"])
def api_set_override():
    data = request.json
    cid = data.get("case_id", "").strip().upper()
    days = int(data.get("interval_days", 7))
    if cid not in registry:
        return jsonify({"ok": False, "error": f"Case {cid} not found"}), 404
    if not 1 <= days <= 30:
        return jsonify({"ok": False, "error": "Interval must be 1-30"}), 400
    CASE_OVERRIDES[cid] = {"interval_days": days}
    return jsonify({"ok": True, "message": f"Override set for {cid}: interval_days={days}"})


@app.route("/api/history/<case_id>", methods=["GET"])
def api_history(case_id):
    cid = case_id.strip().upper()
    if cid not in history:
        return jsonify({"ok": False, "error": f"No history for {cid}"}), 404
    events = [{"seq": seq, "event": event} for seq, event in history[cid].items()]
    return jsonify({"ok": True, "case_id": cid, "events": events})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    injury_counter, missed_by_physio, upcoming_c, missed_c, done_c = stats()
    return jsonify({
        "upcoming": upcoming_c,
        "missed": missed_c,
        "done": done_c,
        "injury_counts": [{"injury": k, "count": v} for k, v in injury_counter.most_common()],
        "missed_by_physio": {p: fids for p, fids in missed_by_physio.items()},
    })


@app.route("/api/audit", methods=["GET"])
def api_audit():
    entries = [{"time": t, "function": fn, "summary": s} for t, fn, s in AUDIT_LOG]
    return jsonify(entries)


@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    generate_demo_data()
    return jsonify({"ok": True, "message": "Demo data regenerated",
                    "cases": len(registry), "followups": len(followups)})


if __name__ == "__main__":
    use_reloader = os.environ.get("FLASK_NO_RELOADER") != "1"
    app.run(debug=True, use_reloader=use_reloader, port=5000)
