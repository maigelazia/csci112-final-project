from flask import Blueprint, render_template, jsonify, request
from routes.admin_auth import admin_required
from services.db_service import appointments_collection, patients_collection
from services.email_service import send_reminder_email, send_cancelled_email
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__)

# HTML VIEWS
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


# pagination helper function
def paginate(cursor, page, page_size):
    start = (page - 1) * page_size
    end = start + page_size
    data = list(cursor)[start:end]
    return data


# APPOINTMENTS API (D1)
@admin_bp.route("/api/admin/appointments", methods=["GET"])
@admin_required
def api_admin_appointments():
    col = appointments_collection()

    # Search / Filter Input
    search = request.args.get("search")
    status = request.args.get("status")
    branch = request.args.get("branch")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_field = request.args.get("sort", "appointment_details.preferred_date")
    order = request.args.get("order", "asc")

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    query = {}

    # SEARCH
    if search:
        query["$or"] = [
            {"patient.full_name": {"$regex": search, "$options": "i"}},
            {"patient.email": {"$regex": search, "$options": "i"}},
            {"appointment_details.concern": {"$regex": search, "$options": "i"}},
            {"appointment_id": {"$regex": search, "$options": "i"}}
        ]

    # FILTER by STATUS
    if status:
        query["appointment_details.status"] = status

    # FILTER by CLINIC BRANCH
    if branch:
        query["appointment_details.clinic_branch"] = branch

    # FILTER by DATE RANGE
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date

    if date_filter:
        query["appointment_details.preferred_date"] = date_filter

    # SORTING
    sort_direction = 1 if order.lower() == "asc" else -1

    cursor = col.find(query, {"_id": 0}).sort(sort_field, sort_direction)

    docs = paginate(cursor, page, page_size)

    return jsonify({
        "page": page,
        "page_size": page_size,
        "count": len(docs),
        "results": docs
    })


# APPOINTMENT STATUS ACTIONS
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


# PATIENTS API (D2)
@admin_bp.route("/api/admin/patients", methods=["GET"])
@admin_required
def api_admin_patients():
    col = patients_collection()

    search = request.args.get("search")
    condition = request.args.get("condition")
    allergy = request.args.get("allergy")
    start_date = request.args.get("created_after")
    end_date = request.args.get("created_before")
    sort_field = request.args.get("sort", "full_name")
    order = request.args.get("order", "asc")

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    query = {}

    # SEARCH
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"contact_number": {"$regex": search, "$options": "i"}},
            {"patient_id": {"$regex": search, "$options": "i"}},
        ]

    # FILTER by MEDICAL CONDITION
    if condition:
        query["conditions.condition"] = {"$regex": condition, "$options": "i"}

    # FILTER by ALLERGY
    if allergy:
        query["allergies.substance"] = {"$regex": allergy, "$options": "i"}

    # CREATED DATE RANGE
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date
    if date_filter:
        query["created_at"] = date_filter

    # SORT
    sort_direction = 1 if order.lower() == "asc" else -1

    cursor = col.find(query, {"_id": 0}).sort(sort_field, sort_direction)

    results = paginate(cursor, page, page_size)

    return jsonify({
        "page": page,
        "page_size": page_size,
        "count": len(results),
        "results": results
    })


# UPDATE APPOINTMENT STATUS 
@admin_bp.route("/api/admin/appointments/<appointment_id>/status", methods=["PUT"])
def update_status(appointment_id):
    data = request.json
    new_status = data.get("status")

    appointments_collection().update_one(
        {"appointment_id": appointment_id},
        {"$set": {"appointment_details.status": new_status}}
    )

    return jsonify({"message": "Status updated"}), 200