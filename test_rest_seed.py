import google.auth
import google.auth.transport.requests
import requests

PROJECT_ID = "qwiklabs-gcp-03-4001ab701a83"

def seed_via_rest():
    credentials, _ = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/plants?documentId=monstera-deliciosa"
    
    body = {
        "fields": {
            "id": {"stringValue": "monstera-deliciosa"},
            "name": {"stringValue": "Monstera Deliciosa"},
            "scientific_name": {"stringValue": "Monstera deliciosa"},
            "care_difficulty": {"stringValue": "Easy"},
            "light_requirement": {"stringValue": "Bright Indirect Light"},
            "watering_frequency_days": {"integerValue": "7"},
            "price": {"doubleValue": 29.99},
            "in_stock": {"booleanValue": True},
            "description": {"stringValue": "Popular tropical plant known for its iconic natural split leaves."}
        }
    }
    
    res = requests.post(url, json=body, headers=headers)
    print("Status:", res.status_code)
    print("Response:", res.text)

if __name__ == "__main__":
    seed_via_rest()
