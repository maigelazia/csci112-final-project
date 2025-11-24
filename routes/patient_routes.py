from flask import Blueprint, request, jsonify
from datetime import datetime
from services.db_service import patients_collection

patient_bp = Blueprint("patient_bp", __name__)

@patient_bp.route("/api/patient", methods=["POST"])
def update_patient_record():
    """Upsert (insert/update) patient record."""
    data = request.get_json()
    patient_id = data.get("patient_id")

    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    data["updated_at"] = datetime.utcnow()

    col = patients_collection()
    col.update_one(
        {"patient_id": patient_id},
        {"$set": data},
        upsert=True
    )

    return jsonify({"message": "Patient record updated successfully."})