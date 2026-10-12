from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        expected_email = current_app.config["ADMIN_EMAIL"].strip().lower()
        expected_password = current_app.config["ADMIN_PASSWORD"]

        if email == expected_email and password == expected_password:
            session.clear()
            session["admin"] = True
            session["admin_email"] = expected_email
            flash("Welcome to the ASEEL admin dashboard.", "success")
            nxt = request.args.get("next") or request.form.get("next") or ""
            if nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("admin.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("public.home"))
