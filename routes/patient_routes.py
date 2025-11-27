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
    return render_template("patient_form.html", appointment_id=appointment_id)

@patient_bp.route("/api/patient", methods=["POST"])
def save_patient():
    data = request.get_json(silent=True) or request.form

    # required minimal fields
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    if not email or not first_name or not last_name:
        return jsonify({"error": "first_name, last_name, and email are required"}), 400

    middle_name = data.get("middle_name")
    full_name = data.get("full_name") or " ".join([x for x in [first_name, middle_name, last_name] if x])
    contact_number = data.get("contact_number")

    pcol = patients_collection()
    existing = pcol.find_one({"email": email})
    now = datetime.utcnow().isoformat()

    if existing:
        patient_id = existing["patient_id"]
    else:
        patient_id = _next_patient_id()

    record = {
        "patient_id": patient_id,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "full_name": full_name,
        "email": email,
        "contact_number": contact_number,

        # optional simple fields
        "address_state": data.get("state"),
        "address_city": data.get("city"),
        "insurance_provider": data.get("insurance_provider"),
        "insurance_policy_number": data.get("insurance_policy_number"),

        # lists/dicts (send as arrays/objects from the form or keep empty)
        "conditions": data.get("conditions", []),          # [{condition, medications, controlled}]
        "allergies": data.get("allergies", []),            # [{substance, reaction}]
        "current_medications": data.get("current_medications", []),
        "family_history": data.get("family_history", {}),  # {diabetes: bool, ...}

        "dental_last_visit": data.get("dental_last_visit"),
        "dental_reason": data.get("dental_reason"),
        "dental_previous_work": data.get("dental_previous_work", []),
        "dental_current_concerns": data.get("dental_current_concerns", []),

        "appointment_history": existing.get("appointment_history", []) if existing else [],

        "created_at": existing.get("created_at") if existing else now,
        "updated_at": now
    }

    # upsert by email
    pcol.update_one({"email": email}, {"$set": record}, upsert=True)

    # if appointment_id provided, attach to appointment + history
    appointment_id = data.get("appointment_id")
    if appointment_id:
        acol = appointments_collection()
        appt = acol.find_one({"appointment_id": appointment_id})
        if appt:
            # attach patient_id to appointment
            acol.update_one(
                {"appointment_id": appointment_id},
                {"$set": {
                    "patient.id": patient_id,
                    "patient.full_name": full_name,
                    "updated_at": now
                }}
            )
            # push a simple entry into patient appointment_history
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

    return jsonify({"message": "Patient record saved.", "patient_id": patient_id})
