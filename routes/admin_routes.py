from flask import Blueprint, jsonify, render_template
from services.db_service import appointments_collection, patients_collection
from routes.admin_auth import admin_required

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

@admin_bp.route("/api/admin/appointments", methods=["GET"])
@admin_required
def all_appointments():
    col = appointments_collection()
    appts = list(col.find({}, {"_id": 0}))
    return jsonify(appts)

@admin_bp.route("/api/admin/patients", methods=["GET"])
@admin_required
def all_patients():
    col = patients_collection()
    pts = list(col.find({}, {"_id": 0}))
    return jsonify(pts)