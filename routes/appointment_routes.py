from flask import Blueprint, request, jsonify, render_template
import uuid
from datetime import datetime

from services.db_service import appointments_collection
from services.email_service import send_confirmation_email, send_patient_form_email

appointment_bp = Blueprint("appointment_bp", __name__)

# Minimal frontend route
@appointment_bp.route("/book", methods=["GET"])
def book_page():
    return render_template("booking.html")

@appointment_bp.route("/api/appointments", methods=["POST"])
def create_appointment():
    """Create appointment and send confirmation email."""
    # Accept JSON or form-encoded body
    data = request.get_json(silent=True) or request.form

    full_name = data.get("full_name")
    email = data.get("email")
    date = data.get("date")
    time = data.get("time")
    concern = data.get("concern")

    if not all([full_name, email, date, time, concern]):
        return jsonify({"error": "full_name, email, date, time, concern are required"}), 400

    appointment_id = "AID" + uuid.uuid4().hex[:10]
    token = uuid.uuid4().hex

    doc = {
        "appointment_id": appointment_id,
        "patient": {
            "full_name": full_name,
            "email": email
        },
        "appointment_details": {
            "preferred_date": date,
            "preferred_time": time,
            "concern": concern,
            "status": "Pending",
            "confirmation_token": token,
            "confirmation_sent_at": datetime.utcnow()
        }
    }

    col = appointments_collection()
    col.insert_one(doc)

    # email confirmation link
    send_confirmation_email(email, token)

    return jsonify({
        "message": "Appointment created. Check your email to confirm.",
        "appointment_id": appointment_id
    }), 201

@appointment_bp.route("/confirm/<token>", methods=["GET"])
def confirm_appointment(token):
    """Confirm appointment from email link."""
    col = appointments_collection()
    appt = col.find_one({"appointment_details.confirmation_token": token})

    if not appt:
        return jsonify({"error": "Invalid or expired confirmation token."}), 400

    col.update_one(
        {"appointment_id": appt["appointment_id"]},
        {"$set": {
            "appointment_details.status": "Confirmed",
            "appointment_details.confirmed_at": datetime.utcnow()
        }}
    )

    # after confirming, send patient form email
    send_patient_form_email(
        appt["patient"]["email"],
        appt["appointment_id"]
    )

    # Minimal confirmation page
    return render_template("confirmation.html")