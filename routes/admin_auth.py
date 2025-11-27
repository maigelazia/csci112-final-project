from flask import Blueprint, render_template, request, redirect, session
import config
from functools import wraps

admin_auth_bp = Blueprint("admin_auth_bp", __name__)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return wrapper

@admin_auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pw = request.form.get("password")
        if pw == config.ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        return render_template("admin_login.html", error="Invalid password.")
    return render_template("admin_login.html")

@admin_auth_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin/login")
