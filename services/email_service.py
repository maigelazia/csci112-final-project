from flask_mail import Message
from flask import current_app
import config

def _get_mail():
    # Flask-Mail registers under app.extensions["mail"]
    return current_app.extensions["mail"]

def send_confirmation_email(email: str, token: str):
    link = f"{config.BASE_URL}/confirm/{token}"
    msg = Message("Confirm Your Appointment", recipients=[email])
    msg.body = f"Please confirm your appointment:\n{link}"
    _get_mail().send(msg)

def send_patient_form_email(email: str, appointment_id: str):
    link = f"{config.BASE_URL}/patient/{appointment_id}"
    msg = Message("Patient Information Form", recipients=[email])
    msg.body = f"Please fill out your patient form:\n{link}"
    _get_mail().send(msg)