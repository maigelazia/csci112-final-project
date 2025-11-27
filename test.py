import requests, json

BASE_URL = "http://127.0.0.1:5000"

def show(resp):
    print("STATUS:", resp.status_code)
    try:
        print("JSON:", json.dumps(resp.json(), indent=2))
    except:
        print("TEXT:", resp.text)
    print("-"*50)

def test_connection():
    print("GET /test")
    show(requests.get(f"{BASE_URL}/test"))

def create_appointment():
    payload = {
        "full_name": "Shoto Todoroki",
        "email": "shoto@example.com",
        "contact_number": "+639123456789",
        "date": "2025-08-01",
        "time": "14:30",
        "concern": "Tooth Extraction",
        "clinic_branch": "Makati Main"
    }
    print("POST /api/appointments")
    resp = requests.post(f"{BASE_URL}/api/appointments", json=payload)
    show(resp)
    try:
        return resp.json().get("appointment_id")
    except:
        return None

def admin_get_appointments():
    print("GET /api/admin/appointments (may need admin session in real app)")
    show(requests.get(f"{BASE_URL}/api/admin/appointments"))

def admin_arrive(appt_id):
    print("POST /api/admin/appointments/{}/arrive".format(appt_id))
    show(requests.post(f"{BASE_URL}/api/admin/appointments/{appt_id}/arrive"))

def admin_complete(appt_id):
    print("POST /api/admin/appointments/{}/complete".format(appt_id))
    show(requests.post(f"{BASE_URL}/api/admin/appointments/{appt_id}/complete"))

def admin_cancel(appt_id):
    print("POST /api/admin/appointments/{}/cancel".format(appt_id))
    show(requests.post(f"{BASE_URL}/api/admin/appointments/{appt_id}/cancel"))

def cancel_link(appt_id):
    print("GET /cancel/{}".format(appt_id))
    show(requests.get(f"{BASE_URL}/cancel/{appt_id}"))

if __name__ == "__main__":
    test_connection()
    appt_id = create_appointment()
    print("APPOINTMENT_ID:", appt_id)
    if appt_id:
        admin_arrive(appt_id)
        admin_complete(appt_id)
        admin_cancel(appt_id)  # or try cancel_link(appt_id)
