import csv
import io
import os
import secrets
from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from auth import login_required
from database import fetch_all, fetch_one, get_db, now_iso
from helpers import parse_threshold, slug_code
from qr_service import generate_qr_image, qr_filename, verification_url

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _base_url():
    configured = current_app.config.get("BASE_URL")
    if configured:
        return configured
    return request.url_root.rstrip("/")


def _qr_path(unique_code):
    return os.path.join(current_app.config["QR_FOLDER"], qr_filename(unique_code))


def _ensure_qr(unique_code):
    path = _qr_path(unique_code)
    generate_qr_image(verification_url(_base_url(), unique_code), path)
    return path


def _new_unique_code(perfume_name=""):
    db = get_db()
    prefix = "ASEEL-" + slug_code(perfume_name)
    while True:
        code = f"{prefix}-{secrets.token_hex(3).upper()}"
        exists = db.execute(
            "SELECT id FROM perfumes WHERE unique_code = ?", (code,)
        ).fetchone()
        if exists is None:
            return code


def _uses_localhost():
    host = (request.host or "").lower()
    return "127.0.0.1" in host or host.startswith("localhost")


def _suggested_serial():
    db = get_db()
    while True:
        serial = "ASEEL-BOX-" + secrets.token_hex(3).upper()
        exists = db.execute(
            "SELECT id FROM perfumes WHERE box_serial_number = ?", (serial,)
        ).fetchone()
        if exists is None:
            return serial


def _perfume_form(defaults=None):
    keys = [
        "perfume_name",
        "brand_name",
        "batch_number",
        "box_serial_number",
        "manufacturing_date",
        "authorized_seller",
        "place_of_sale",
        "status",
        "scan_threshold",
        "notes",
    ]
    source = defaults or {}
    form = {}
    for key in keys:
        if request.method == "POST":
            form[key] = (request.form.get(key) or "").strip()
        elif hasattr(source, "keys"):
            value = source[key] if key in source.keys() else ""
            form[key] = "" if value is None else str(value)
        else:
            form[key] = ""
    if not form["status"]:
        form["status"] = "Genuine"
    if not form["scan_threshold"]:
        form["scan_threshold"] = str(current_app.config["DEFAULT_SCAN_THRESHOLD"])
    if request.method != "POST" and not form["box_serial_number"]:
        form["box_serial_number"] = _suggested_serial()
    return form


@admin_bp.route("/")
@login_required
def dashboard():
    db = get_db()
    total_perfumes = db.execute("SELECT COUNT(*) AS n FROM perfumes").fetchone()["n"]
    total_scans = db.execute("SELECT COALESCE(SUM(scan_count), 0) AS n FROM perfumes").fetchone()["n"]
    suspicious = db.execute(
        """
        SELECT COUNT(*) AS n FROM perfumes
        WHERE status = 'Suspicious' OR scan_count > scan_threshold
        """
    ).fetchone()["n"]
    not_verified = db.execute("SELECT COUNT(*) AS n FROM invalid_scan_logs").fetchone()["n"]
    disabled = db.execute(
        "SELECT COUNT(*) AS n FROM perfumes WHERE status = 'Disabled'"
    ).fetchone()["n"]

    recent_scans = fetch_all(
        """
        SELECT scanned_at, unique_code, result_status, perfume_id
        FROM (
            SELECT scanned_at, unique_code, result_status, perfume_id FROM scan_logs
            UNION ALL
            SELECT scanned_at, attempted_code AS unique_code, result_status, NULL AS perfume_id
            FROM invalid_scan_logs
        )
        ORDER BY scanned_at DESC
        LIMIT 8
        """
    )
    query = (request.args.get("q") or "").strip()
    status_filter = (request.args.get("status") or "").strip()
    clauses = []
    params = []
    if query:
        like = f"%{query}%"
        clauses.append(
            """(
                perfume_name LIKE ? OR brand_name LIKE ? OR unique_code LIKE ?
                OR box_serial_number LIKE ? OR batch_number LIKE ?
            )"""
        )
        params.extend([like, like, like, like, like])
    if status_filter in {"Genuine", "Suspicious", "Disabled"}:
        clauses.append("status = ?")
        params.append(status_filter)
    sql = "SELECT * FROM perfumes"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY created_at DESC"
    perfumes = fetch_all(sql, tuple(params))
    return render_template(
        "admin/dashboard.html",
        total_perfumes=total_perfumes,
        total_scans=total_scans,
        suspicious=suspicious,
        not_verified=not_verified,
        disabled=disabled,
        recent_scans=recent_scans,
        perfumes=perfumes,
        query=query,
        status_filter=status_filter,
        uses_localhost=_uses_localhost(),
        public_host=request.host,
    )


@admin_bp.route("/scans")
@login_required
def scan_activity():
    result_filter = (request.args.get("result") or "").strip()
    logs = fetch_all(
        """
        SELECT scanned_at, unique_code, result_status, perfume_id, notes
        FROM (
            SELECT scanned_at, unique_code, result_status, perfume_id, notes FROM scan_logs
            UNION ALL
            SELECT scanned_at, attempted_code AS unique_code, result_status, NULL AS perfume_id,
                   NULL AS notes
            FROM invalid_scan_logs
        )
        ORDER BY scanned_at DESC
        LIMIT 200
        """
    )
    if result_filter:
        logs = [row for row in logs if row["result_status"] == result_filter]
    return render_template(
        "admin/scans.html",
        logs=logs,
        result_filter=result_filter,
    )


@admin_bp.route("/export.csv")
@login_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "unique_code",
            "perfume_name",
            "brand_name",
            "batch_number",
            "box_serial_number",
            "manufacturing_date",
            "authorized_seller",
            "place_of_sale",
            "status",
            "scan_count",
            "scan_threshold",
            "created_at",
        ]
    )
    for row in fetch_all("SELECT * FROM perfumes ORDER BY id"):
        writer.writerow(
            [
                row["unique_code"],
                row["perfume_name"],
                row["brand_name"],
                row["batch_number"],
                row["box_serial_number"],
                row["manufacturing_date"],
                row["authorized_seller"],
                row["place_of_sale"],
                row["status"],
                row["scan_count"],
                row["scan_threshold"],
                row["created_at"],
            ]
        )
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=aseel-perfumes.csv"},
    )


@admin_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        form = _perfume_form()
        required = [
            "perfume_name",
            "brand_name",
            "batch_number",
            "box_serial_number",
            "manufacturing_date",
            "authorized_seller",
            "place_of_sale",
            "status",
        ]
        if any(not form[field] for field in required):
            flash("Please complete all required fields.", "error")
            return render_template("admin/register.html", form=form)

        existing = fetch_one(
            "SELECT id FROM perfumes WHERE box_serial_number = ?",
            (form["box_serial_number"],),
        )
        if existing:
            flash("That box / serial number is already registered. Each bottle needs a unique serial.", "error")
            return render_template("admin/register.html", form=form)

        unique_code = _new_unique_code(form["perfume_name"])
        timestamp = now_iso()
        threshold = parse_threshold(
            form["scan_threshold"], current_app.config["DEFAULT_SCAN_THRESHOLD"]
        )
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO perfumes (
                unique_code, perfume_name, brand_name, batch_number,
                box_serial_number, manufacturing_date, authorized_seller,
                place_of_sale, status, scan_count, scan_threshold, notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
            """,
            (
                unique_code,
                form["perfume_name"],
                form["brand_name"],
                form["batch_number"],
                form["box_serial_number"],
                form["manufacturing_date"],
                form["authorized_seller"],
                form["place_of_sale"],
                form["status"],
                threshold,
                form["notes"] or None,
                timestamp,
                timestamp,
            ),
        )
        db.commit()
        _ensure_qr(unique_code)
        flash("Perfume record saved. A unique QR code has been generated.", "success")
        return redirect(url_for("admin.product_detail", perfume_id=cursor.lastrowid))

    return render_template("admin/register.html", form=_perfume_form())


@admin_bp.route("/products/<int:perfume_id>")
@login_required
def product_detail(perfume_id):
    perfume = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume_id,))
    if perfume is None:
        flash("Perfume record not found.", "error")
        return redirect(url_for("admin.dashboard"))

    _ensure_qr(perfume["unique_code"])
    logs = fetch_all(
        "SELECT * FROM scan_logs WHERE perfume_id = ? ORDER BY scanned_at DESC",
        (perfume_id,),
    )
    return render_template(
        "admin/product.html",
        perfume=perfume,
        logs=logs,
        public_url=verification_url(_base_url(), perfume["unique_code"]),
        qr_file=qr_filename(perfume["unique_code"]),
        uses_localhost=_uses_localhost(),
    )


@admin_bp.route("/products/<int:perfume_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(perfume_id):
    perfume = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume_id,))
    if perfume is None:
        flash("Perfume record not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        form = _perfume_form()
        threshold = parse_threshold(form["scan_threshold"], perfume["scan_threshold"])
        duplicate = fetch_one(
            "SELECT id FROM perfumes WHERE box_serial_number = ? AND id != ?",
            (form["box_serial_number"], perfume_id),
        )
        required = [
            "perfume_name",
            "brand_name",
            "batch_number",
            "box_serial_number",
            "manufacturing_date",
            "authorized_seller",
            "place_of_sale",
            "status",
        ]
        if any(not form[field] for field in required):
            flash("Please complete all required fields.", "error")
            return render_template("admin/edit.html", perfume=perfume, form=form)
        if duplicate:
            flash("Another record already uses that box / serial number.", "error")
            return render_template("admin/edit.html", perfume=perfume, form=form)

        db = get_db()
        db.execute(
            """
            UPDATE perfumes SET
                perfume_name = ?, brand_name = ?, batch_number = ?,
                box_serial_number = ?, manufacturing_date = ?, authorized_seller = ?,
                place_of_sale = ?, status = ?, scan_threshold = ?, notes = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                form["perfume_name"],
                form["brand_name"],
                form["batch_number"],
                form["box_serial_number"],
                form["manufacturing_date"],
                form["authorized_seller"],
                form["place_of_sale"],
                form["status"],
                threshold,
                form["notes"] or None,
                now_iso(),
                perfume_id,
            ),
        )
        db.commit()
        flash("Product details updated.", "success")
        return redirect(url_for("admin.product_detail", perfume_id=perfume_id))

    return render_template("admin/edit.html", perfume=perfume, form=_perfume_form(perfume))


@admin_bp.route("/products/<int:perfume_id>/status", methods=["POST"])
@login_required
def update_status(perfume_id):
    status = request.form.get("status")
    if status not in {"Genuine", "Suspicious", "Disabled"}:
        flash("Invalid status.", "error")
        return redirect(url_for("admin.product_detail", perfume_id=perfume_id))

    db = get_db()
    db.execute(
        "UPDATE perfumes SET status = ?, updated_at = ? WHERE id = ?",
        (status, now_iso(), perfume_id),
    )
    db.commit()
    flash(f"Product marked as {status}.", "success")
    return redirect(url_for("admin.product_detail", perfume_id=perfume_id))


@admin_bp.route("/products/<int:perfume_id>/reset-scans", methods=["POST"])
@login_required
def reset_scans(perfume_id):
    perfume = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume_id,))
    if perfume is None:
        flash("Perfume record not found.", "error")
        return redirect(url_for("admin.dashboard"))
    db = get_db()
    db.execute(
        "UPDATE perfumes SET scan_count = 0, status = 'Genuine', updated_at = ? WHERE id = ?",
        (now_iso(), perfume_id),
    )
    db.commit()
    flash("Scan count reset and status restored to Genuine for the demo.", "success")
    return redirect(url_for("admin.product_detail", perfume_id=perfume_id))


@admin_bp.route("/products/<int:perfume_id>/qr.png")
@login_required
def download_qr(perfume_id):
    perfume = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume_id,))
    if perfume is None:
        flash("Perfume record not found.", "error")
        return redirect(url_for("admin.dashboard"))
    path = _ensure_qr(perfume["unique_code"])
    return send_file(
        path,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"ASEEL-{perfume['box_serial_number']}.png",
    )


@admin_bp.route("/products/<int:perfume_id>/qr")
@login_required
def print_qr(perfume_id):
    perfume = fetch_one("SELECT * FROM perfumes WHERE id = ?", (perfume_id,))
    if perfume is None:
        flash("Perfume record not found.", "error")
        return redirect(url_for("admin.dashboard"))
    _ensure_qr(perfume["unique_code"])
    return render_template(
        "admin/print_qr.html",
        perfume=perfume,
        public_url=verification_url(_base_url(), perfume["unique_code"]),
        qr_file=qr_filename(perfume["unique_code"]),
    )
