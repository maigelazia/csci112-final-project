from datetime import datetime, timedelta
from services.db_service import appointments_collection
from services.email_service import send_reminder_email, send_cancelled_email
from config import Config

# send reminders every day at 8 AM for appointments happening tomorrow
def send_daily_reminders():
    col = appointments_collection()

    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    # preferred_date stored as "YYYY-MM-DD"
    appts = col.find({
        "appointment_details.preferred_date": str(tomorrow),
        "appointment_details.status": "Pending"
    })

    for appt in appts:
        email = appt["patient"]["email"]
        send_reminder_email(email, appt)


# auto-cancel expired appointments
def cancel_expired_appointments():
    col = appointments_collection()

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    expired = col.find({
        "appointment_details.preferred_date": str(yesterday),
        "appointment_details.status": "Pending"
    })

    for appt in expired:
        appointment_id = appt["appointment_id"]

        # update DB
        col.update_one(
            {"appointment_id": appointment_id},
            {"$set": {
                "appointment_details.status": "Cancelled",
                "updated_at": datetime.utcnow()
            }}
        )

        # notify patient
        send_no_show_email(
            appt["patient"]["email"],
            appointment_id
        )
