from flask import Blueprint, render_template, jsonify
from routes.admin_auth import admin_required
from services.db_service import appointments_collection, patients_collection
from services.email_service import send_reminder_email, send_cancelled_email
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__)

# HTML Views
@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    return render_template("admin_appointments.html")

@admin_bp.route("/admin/appointments")
@admin_required
def view_appointments():
    return render_template("admin_appointments.html")

@admin_bp.route("/admin/patients")
@admin_required
def view_patients():
    return render_template("admin_patients.html")

# JSON APIs
@admin_bp.route("/api/admin/appointments")
@admin_required
def api_admin_appointments():
    docs = list(appointments_collection().find({}, {"_id": 0}))
    return jsonify(docs)

@admin_bp.route("/api/admin/patients")
@admin_required
def api_admin_patients():
    docs = list(patients_collection().find({}, {"_id": 0}))
    return jsonify(docs)

# Status actions
@admin_bp.route("/api/admin/appointments/<appointment_id>/arrive", methods=["POST"])
@admin_required
def mark_arrived(appointment_id):
    res = appointments_collection().update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "appointment_details.status": "Arrived",
            "appointment_details.check_in.arrived": True,
            "appointment_details.check_in.arrival_time": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    if res.matched_count == 0:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify({"message": "Patient marked as arrived."})

@admin_bp.route("/api/admin/appointments/<appointment_id>/complete", methods=["POST"])
@admin_required
def mark_completed(appointment_id):
    res = appointments_collection().update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "appointment_details.status": "Completed",
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    if res.matched_count == 0:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify({"message": "Appointment marked as completed."})

@admin_bp.route("/api/admin/appointments/<appointment_id>/cancel", methods=["POST"])
@admin_required
def mark_cancelled(appointment_id):
    col = appointments_collection()
    appt = col.find_one({"appointment_id": appointment_id})
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404

    col.update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "appointment_details.status": "Cancelled",
            "appointment_details.cancelled_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    send_cancelled_email(appt["patient"]["email"], appointment_id)
    return jsonify({"message": "Appointment cancelled and email sent."})

@admin_bp.route("/api/admin/appointments/<appointment_id>/send-reminder", methods=["POST"])
@admin_required
def send_reminder(appointment_id):
    col = appointments_collection()
    appt = col.find_one({"appointment_id": appointment_id})
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404

    send_reminder_email(appt["patient"]["email"], appt)
    return jsonify({"message": "Reminder email sent."})
