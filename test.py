import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def print_response(resp):
    print("STATUS:", resp.status_code)
    try:
        print("JSON:", resp.json())
    except Exception:
        print("TEXT:", resp.text)
    print("-" * 40)


def test_connection():
    print("- Testing /test route")
    resp = requests.get(f"{BASE_URL}/test")
    print_response(resp)


def test_create_appointment():
    print("- Testing POST /api/appointments")
    data = {
        "full_name": "John Tester",
        "email": "john@test.com",
        "date": "2025-01-20",
        "time": "14:00",
        "concern": "Testing API"
    }
    resp = requests.post(
        f"{BASE_URL}/api/appointments",
        json=data
    )
    print_response(resp)

    # Return appointment_id if created
    try:
        return resp.json().get("appointment_id")
    except:
        return None


def test_get_appointments():
    print("- Testing GET /api/admin/appointments")
    resp = requests.get(f"{BASE_URL}/api/admin/appointments")
    print_response(resp)


def test_patient_record():
    print("- Testing POST /api/patient")
    data = {
        "patient_id": "PID001",
        "first_name": "Test",
        "last_name": "User",
        "medical_history": "None"
    }

    resp = requests.post(
        f"{BASE_URL}/api/patient",
        json=data
    )
    print_response(resp)


if __name__ == "__main__":
    print("=== Running API Tests ===")

    test_connection()
    test_get_appointments()

    appt_id = test_create_appointment()
    print("Created Appointment ID:", appt_id)

    test_patient_record()

    print("=== Tests Complete ===")