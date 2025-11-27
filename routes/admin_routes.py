from flask import Blueprint, jsonify, render_template
from services.db_service import appointments_collection, patients_collection
from routes.admin_auth import admin_required

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_base.html")

@admin_bp.route("/admin/appointments")
@admin_required
def view_appointments():
    return render_template("admin_appointments.html")

@admin_bp.route("/admin/patients")
@admin_required
def view_patients():
    return render_template("admin_patients.html")