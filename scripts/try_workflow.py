from fastapi.testclient import TestClient

from appointment_search.service import app


client = TestClient(app)

indexed = client.post(
    "/guidance",
    json={
        "documents": [
            {
                "document_id": "imaging-prep-2026",
                "title": "Imaging appointment preparation",
                "text": "Arrive 20 minutes early and bring a photo ID and medication list.",
            }
        ]
    },
)
indexed.raise_for_status()

planned = client.post(
    "/appointments/notification",
    json={
        "patient_first_name": "Riley",
        "appointment_time": "Tuesday at 09:30",
        "visit_type": "imaging",
    },
)
planned.raise_for_status()
print(planned.json())
