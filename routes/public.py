from flask import Blueprint, current_app, render_template, request, redirect, url_for
from database import fetch_one, get_db, now_iso
from helpers import normalize_code

public_bp = Blueprint("public", __name__)


def _user_agent():
    return (request.headers.get("User-Agent") or "")[:400]


def _log_invalid(code, result_status):
    db = get_db()
    db.execute(
        """
        INSERT INTO invalid_scan_logs (attempted_code, scanned_at, result_status, user_agent)
        VALUES (?, ?, ?, ?)
        """,
        (code, now_iso(), result_status, _user_agent()),
    )
    db.commit()


def _log_scan(perfume_id, unique_code, result_status, notes=None):
    db = get_db()
    db.execute(
        """
        INSERT INTO scan_logs (perfume_id, unique_code, scanned_at, result_status, user_agent, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (perfume_id, unique_code, now_iso(), result_status, _user_agent(), notes),
    )
    db.commit()


@public_bp.route("/")
def home():
    return render_template("home.html")


@public_bp.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


@public_bp.route("/verify", methods=["GET", "POST"])
def verify_lookup():
    if request.method == "POST":
        code = normalize_code(request.form.get("code"))
        if code:
            return redirect(url_for("public.verify", unique_code=code))
    return render_template("verify_lookup.html")


@public_bp.route("/verify/<unique_code>")
def verify(unique_code):
    code = normalize_code(unique_code)
    perfume = fetch_one("SELECT * FROM perfumes WHERE unique_code = ?", (code,))

    if perfume is None:
        _log_invalid(code, "Not Verified")
        return render_template(
            "verify.html",
            state="not_found",
            unique_code=code,
            perfume=None,
            scan_count=None,
        )

    db = get_db()

    if perfume["status"] == "Disabled":
        db.execute(
            "UPDATE perfumes SET scan_count = scan_count + 1, updated_at = ? WHERE id = ?",
            (now_iso(), perfume["id"]),
        )
        db.commit()
        updated = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume["id"],))
        _log_scan(perfume["id"], code, "Disabled", "Authentication code is no longer active.")
        return render_template(
            "verify.html",
            state="disabled",
            unique_code=code,
            perfume=updated,
            scan_count=updated["scan_count"],
        )

    db.execute(
        "UPDATE perfumes SET scan_count = scan_count + 1, updated_at = ? WHERE id = ?",
        (now_iso(), perfume["id"]),
    )
    db.commit()
    updated = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume["id"],))

    threshold = updated["scan_threshold"] or current_app.config["DEFAULT_SCAN_THRESHOLD"]
    over_threshold = updated["scan_count"] > threshold
    if over_threshold and updated["status"] == "Genuine":
        db.execute(
            "UPDATE perfumes SET status = 'Suspicious', updated_at = ? WHERE id = ?",
            (now_iso(), updated["id"]),
        )
        db.commit()
        updated = fetch_one("SELECT * FROM perfumes WHERE id = ?", (updated["id"],))

    if over_threshold or updated["status"] == "Suspicious":
        note = (
            "Scan count exceeded the authenticity threshold."
            if over_threshold
            else "Product is currently marked as Suspicious."
        )
        _log_scan(updated["id"], code, "Warning", note)
        return render_template(
            "verify.html",
            state="warning",
            unique_code=code,
            perfume=updated,
            scan_count=updated["scan_count"],
        )

    _log_scan(updated["id"], code, "Verified", "Within normal scan threshold.")
    return render_template(
        "verify.html",
        state="verified",
        unique_code=code,
        perfume=updated,
        scan_count=updated["scan_count"],
    )
