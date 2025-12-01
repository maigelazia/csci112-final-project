import random
from datetime import datetime, timedelta
from services.db_service import appointments_collection, patients_collection


FIRST_NAMES = [
    "John", "Maria", "Carlos", "Elijah", "Isabella", "Sophia", "Miguel", "Daniel",
    "Nathan", "Chloe", "Julia", "Patrick", "Christian", "Aaliyah", "Gabriel",
    "Anthony", "Leo", "Oliver", "Samuel", "James", "Hannah", "Grace", "Nicole",
    "Adrian", "Jerome", "Joshua", "Kimberly", "Diane", "Michelle"
]

LAST_NAMES = [
    "Garcia", "Cruz", "Reyes", "Santos", "Torres", "Ramirez", "Johnson", "Smith",
    "Williams", "Brown", "Jones", "Davis", "Lopez", "Miller", "Martinez",
    "Anderson", "Flores", "Hill", "Cooper", "Bailey"
]

CONCERNS = [
    "Cleaning", "Tooth Extraction", "Root Canal", "Orthodontics", "Consultation",
    "Dental Implants", "Wisdom Tooth Removal", "Filling", "Crown Checkup"
]

BRANCHES = [
    "Makati Main Clinic",
    "BGC Dental Center",
    "Quezon City Branch",
    "Manila Downtown Clinic",
    "Pasig-Ortigas Dental Hub"
]

MED_CONDITIONS = [
    "Diabetes", "Hypertension", "Asthma", "Allergies", "Heart Disease",
    "Thyroid Issues", "Arthritis", "Depression", "Anxiety"
]

ALLERGIES = [
    "Penicillin", "Aspirin", "Latex", "Pollen", "Dust Mites",
    "Food Allergies", "Insect Stings"
]

def generate_patient_id(n):
    return f"PID{str(n).zfill(10)}"


def generate_appointment_id(n):
    return f"AID{str(n).zfill(10)}"


def seed_patients(count=150):
    col = patients_collection()
    existing = col.count_documents({})

    print(f"[D2] Patients existing: {existing}")

    if existing >= count:
        print("[D2] Patients already seeded. Skipping.")
        return

    print(f"[D2] Seeding {count - existing} patients...")

    bulk_data = []
    now = datetime.utcnow().isoformat()

    for i in range(existing + 1, count + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"

        patient_id = generate_patient_id(i)
        email = f"{first.lower()}.{last.lower()}{i}@mail.com"
        contact_number = f"+639{random.randint(100000000, 999999999)}"

        num_conditions = random.randint(0, 3)
        patient_conditions = random.sample(MED_CONDITIONS, k=min(num_conditions, len(MED_CONDITIONS)))
        
        num_allergies = random.randint(0, 2)
        patient_allergies = random.sample(ALLERGIES, k=min(num_allergies, len(ALLERGIES)))

        doc = {
            "patient_id": patient_id,
            "full_name": full_name,
            "email": email,
            "contact_number": contact_number,

            "address_state": "Metro Manila",
            "address_city": random.choice(["Makati", "Taguig", "QC", "Pasig", "Manila"]),

            "insurance_provider": "PhilHealth",
            "insurance_policy_number": f"PH{random.randint(1000000000, 9999999999)}",

            "conditions": patient_conditions,
            "allergies": patient_allergies,
            "current_medications": [],
            "family_history": {},

            "dental_last_visit": None,
            "dental_reason": None,
            "dental_previous_work": [],
            "dental_current_concerns": [],

            "appointment_history": [],

            "created_at": now,
            "updated_at": now
        }

        bulk_data.append(doc)

    if bulk_data:
        col.insert_many(bulk_data)

    print("[D2] Patient seeding complete.")


def seed_appointments(count=500):
    col = appointments_collection()
    pcol = patients_collection()

    existing = col.count_documents({})
    print(f"[D1] Appointments existing: {existing}")

    if existing >= count:
        print("[D1] Appointments already seeded. Skipping.")
        return

    print(f"[D1] Seeding {count - existing} appointments...")

    patients = list(pcol.find({}))
    bulk_appts = []
    bulk_history_updates = []

    for i in range(existing + 1, count + 1):
        patient = random.choice(patients)

        appointment_id = generate_appointment_id(i)
        full_name = patient["full_name"]

        days_offset = random.randint(-30, 30)
        appt_date = (datetime.utcnow() + timedelta(days=days_offset)).date()
        appt_time = f"{random.randint(9, 16)}:00"

        concern = random.choice(CONCERNS)
        branch = random.choice(BRANCHES)
        status = random.choice(["Pending", "Arrived", "Completed", "Cancelled"])

        now = datetime.utcnow().isoformat()

        appt_doc = {
            "appointment_id": appointment_id,
            "patient": {
                "id": patient["patient_id"],
                "full_name": full_name,
                "email": patient["email"],
                "contact_number": patient["contact_number"]
            },
            "appointment_details": {
                "preferred_date": str(appt_date),
                "preferred_time": appt_time,
                "concern": concern,
                "clinic_branch": branch,
                "status": status,
                "check_in": {
                    "arrived": status == "Arrived",
                    "arrival_time": now if status == "Arrived" else None
                }
            },
            "created_at": now,
            "updated_at": now
        }

        bulk_appts.append(appt_doc)

        history_entry = {
            "$push": {
                "appointment_history": {
                    "appointment_id": appointment_id,
                    "date": str(appt_date),
                    "time": appt_time,
                    "concern": concern,
                    "branch": branch,
                    "status": status
                }
            }
        }

        bulk_history_updates.append((patient["patient_id"], history_entry))

    # insert all appointments
    if bulk_appts:
        col.insert_many(bulk_appts)

    # update patient history in bulk
    for pid, update in bulk_history_updates:
        pcol.update_one({"patient_id": pid}, update)

    print("[D1] Appointment seeding complete.")


def wipe_data():
    print("Starting Database Wipe")
    
    appt_col = appointments_collection()
    patient_col = patients_collection()

    deleted_appts = appt_col.delete_many({})
    print(f"[D1] Successfully deleted {deleted_appts.deleted_count} appointments.")
    
    deleted_patients = patient_col.delete_many({})
    print(f"[D2] Successfully deleted {deleted_patients.deleted_count} patients.")

    print("--- Database Wipe Complete ---")


if __name__ == "__main__":
    # can remove this line if we dont want to wipe data
    wipe_data()

    seed_patients()
    seed_appointments()