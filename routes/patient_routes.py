from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from services.db_service import patients_collection, appointments_collection

patient_bp = Blueprint("patient_bp", __name__)

def _next_patient_id():
    # simple sequential id: PID + zero-padded count+1
    count = patients_collection().estimated_document_count() + 1
    return f"PID{count:010d}"

@patient_bp.route("/patient/<appointment_id>")
def patient_form_page(appointment_id):
    appt = appointments_collection().find_one({"appointment_id": appointment_id})
    if not appt:
        return "Invalid appointment", 404

    # pass existing data to frontend so fields can be pre-filled or hidden
    patient_info = appt["patient"]

    return render_template(
        "patient_form.html",
        appointment_id=appointment_id,
        patient_info=patient_info
    )

@patient_bp.route("/api/patient", methods=["POST"])
def save_patient():
    data = request.get_json(silent=True) or request.form

    appointment_id = data.get("appointment_id")
    if not appointment_id:
        return jsonify({"error": "appointment_id required"}), 400

    # load appointment so we can pull patient name/email/contact from it
    acol = appointments_collection()
    appt = acol.find_one({"appointment_id": appointment_id})
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404

    full_name = appt["patient"]["full_name"]
    email = appt["patient"]["email"]
    contact_number = appt["patient"].get("contact_number")

    pcol = patients_collection()
    existing = pcol.find_one({"email": email})
    now = datetime.utcnow().isoformat()

    if existing:
        patient_id = existing["patient_id"]
    else:
        patient_id = _next_patient_id()

    # build clean patient record
    record = {
        "patient_id": patient_id,
        "full_name": full_name,
        "email": email,
        "contact_number": contact_number,

        "address": {
            "state": data.get("address_state"),
            "city": data.get("address_city")
        },

        "insurance_details": {
            "provider": data.get("insurance_provider"),
            "policy_number": data.get("insurance_policy_number")
        },

        "medical_history": {
            "conditions": data.get("conditions", []),
            "allergies": data.get("allergies", []),
            "current_medications": data.get("current_medications", []),
            "family_history": data.get("family_history", {})
        },

        "dental_history": {
            "last_visit": data.get("dental_last_visit"),
            "reason_for_visit": data.get("dental_reason"),
            "previous_dental_work": data.get("dental_previous_work", []),
            "current_concerns": data.get("dental_current_concerns", [])
        },

        "appointment_history": existing.get("appointment_history", []) if existing else [],

        "created_at": existing.get("created_at", now) if existing else now,
        "updated_at": now
    }

    # upsert
    pcol.update_one({"email": email}, {"$set": record}, upsert=True)

    # attach patient_id to appointment
    acol.update_one(
        {"appointment_id": appointment_id},
        {"$set": {
            "patient.id": patient_id,
            "patient.full_name": full_name,
            "updated_at": now
        }}
    )

    # log entry to history
    entry = {
        "appointment_id": appointment_id,
        "date": appt["appointment_details"].get("preferred_date"),
        "time": appt["appointment_details"].get("preferred_time"),
        "concern": appt["appointment_details"].get("concern"),
        "branch": appt["appointment_details"].get("clinic_branch"),
        "status": appt["appointment_details"].get("status")
    }

    pcol.update_one(
        {"email": email},
        {"$addToSet": {"appointment_history": entry},
         "$set": {"updated_at": now}}
    )

    return jsonify({"message": "Patient record saved", "patient_id": patient_id})
