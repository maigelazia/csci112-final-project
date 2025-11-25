from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from services.db_service import patients_collection

patient_bp = Blueprint("patient_bp", __name__)

# Minimal frontend route
@patient_bp.route("/patient/<appointment_id>", methods=["GET"])
def patient_form_page(appointment_id):
    return render_template("patient_form.html", appointment_id=appointment_id)

@patient_bp.route("/api/patient", methods=["POST"])
def update_patient_record():
    """Upsert patient record. Keyed by patient_id."""
    data = request.get_json(silent=True) or request.form

    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    record = {
        "patient_id": patient_id,
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "medical_history": data.get("medical_history"),
        "updated_at": datetime.utcnow()
    }

    col = patients_collection()
    col.update_one(
        {"patient_id": patient_id},
        {"$set": record},
        upsert=True
    )

    return jsonify({"message": "Patient record updated successfully."})