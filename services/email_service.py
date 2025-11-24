from flask_mail import Message
from app import mail

BASE_URL = "http://localhost:5000"

def send_confirmation_email(email: str, token: str):
    link = f"{BASE_URL}/confirm/{token}"
    msg = Message("Confirm Your Appointment", recipients=[email])
    msg.body = f"Please confirm your appointment:\n{link}"
    mail.send(msg)

def send_patient_form_email(email: str, appointment_id: str):
    link = f"{BASE_URL}/patient/{appointment_id}"
    msg = Message("Patient Information Form", recipients=[email])
    msg.body = f"Please fill out your patient form:\n{link}"
    mail.send(msg)