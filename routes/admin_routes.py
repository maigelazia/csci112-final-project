from flask import Blueprint, jsonify, render_template
from routes.admin_auth import admin_required
from services.db_service import appointments_collection, patients_collection

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    return render_template("admin_base.html")

@admin_bp.route("/admin/appointments")
@admin_required
def view_appointments():
    return render_template("admin_appointments.html")

@admin_bp.route("/admin/patients")
@admin_required
def view_patients():
    return render_template("admin_patients.html")

# JSON APIs the pages fetch() on load
@admin_bp.route("/api/admin/appointments")
@admin_required
def api_admin_appointments():
    col = appointments_collection()
    docs = list(col.find({}, {"_id": 0}))
    return jsonify(docs)

@admin_bp.route("/api/admin/patients")
@admin_required
def api_admin_patients():
    col = patients_collection()
    docs = list(col.find({}, {"_id": 0}))
    return jsonify(docs)