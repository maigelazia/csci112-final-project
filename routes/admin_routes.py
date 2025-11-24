from flask import Blueprint, jsonify
from services.db_service import appointments_collection, patients_collection

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/api/admin/appointments", methods=["GET"])
def all_appointments():
    col = appointments_collection()
    appts = list(col.find({}, {"_id": 0}))
    return jsonify(appts)

@admin_bp.route("/api/admin/patients", methods=["GET"])
def all_patients():
    col = patients_collection()
    pts = list(col.find({}, {"_id": 0}))
    return jsonify(pts)