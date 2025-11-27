from flask_mail import Message
from flask import current_app
import config

def _mail():
    # Flask-Mail registers as an extension
    return current_app.extensions["mail"]

def send_patient_form_email(email: str, appointment_id: str):
    link = f"{config.BASE_URL}/patient/{appointment_id}"
    msg = Message("Patient Information Form", recipients=[email])
    msg.body = f"Please fill out your patient information form:\n{link}"
    _mail().send(msg)

def send_reminder_email(email: str, appointment: dict):
    cancel_link = f"{config.BASE_URL}/cancel/{appointment['appointment_id']}"
    details = appointment["appointment_details"]
    msg = Message("Appointment Reminder", recipients=[email])
    msg.body = (
        f"Reminder for your appointment:\n"
        f"Date: {details.get('preferred_date')}\n"
        f"Time: {details.get('preferred_time')}\n"
        f"Branch: {details.get('clinic_branch')}\n\n"
        f"If you need to cancel, click:\n{cancel_link}"
    )
    _mail().send(msg)

def send_cancelled_email(email: str, appointment_id: str):
    msg = Message("Appointment Cancelled", recipients=[email])
    msg.body = (
        f"Your appointment ({appointment_id}) has been cancelled.\n"
        f"If this was a mistake, please book again."
    )
    _mail().send(msg)

