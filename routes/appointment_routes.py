from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import uuid

from services.db_service import appointments_collection, patients_collection
from services.email_service import (
    send_patient_form_email,
    send_cancelled_email
)

appointment_bp = Blueprint("appointment_bp", __name__)


@appointment_bp.route("/book")
def book_page():
    return render_template("booking.html")

# create appointment
@appointment_bp.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json(silent=True) or request.form

    full_name = data.get("full_name")
    email = data.get("email")
    contact_number = data.get("contact_number")
    date = data.get("date")
    time = data.get("time")
    concern = data.get("concern")
    clinic_branch = data.get("clinic_branch", "Main")

    if not all([full_name, email, date, time, concern]):
        return jsonify({"error": "Missing required fields: full_name, email, date, time, concern"}), 400

    appointment_id = "AID" + uuid.uuid4().hex[:12].upper()

    doc = {
        "appointment_id": appointment_id,
        "patient": {
            "id": None,  # will be filled when/if patient form is submitted
            "full_name": full_name,
            "email": email,
            "contact_number": contact_number
        },
        "appointment_details": {
            "preferred_date": date,
            "preferred_time": time,
            "concern": concern,
            "clinic_branch": clinic_branch,
            "status": "Pending",
            "check_in": {
                "arrived": False,
                "arrival_time": None
            }
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    appointments_collection().insert_one(doc)

    # if this is a new email (no patient record yet), send patient form email
    if not patients_collection().find_one({"email": email}):
        send_patient_form_email(email, appointment_id)

    return jsonify({
        "message": "Appointment created.",
        "appointment_id": appointment_id,
        "new_patient": not bool(patients_collection().find_one({"email": email}))
    }), 201

# cancellation link
@appointment_bp.route("/cancel/<appointment_id>")
def cancel_appointment(appointment_id):
    col = appointments_collection()
    appt = col.find_one({"appointment_id": appointment_id})
    if not appt:
        return render_template("cancelled.html", appointment_id=None, error="Invalid or expired link.")

    col.update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "appointment_details.status": "Cancelled",
            "appointment_details.cancelled_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }}
    )

    send_cancelled_email(appt["patient"]["email"], appointment_id)
    return render_template("cancelled.html", appointment_id=appointment_id, error=None)
