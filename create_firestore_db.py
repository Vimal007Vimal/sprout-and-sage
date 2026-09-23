import google.auth
import google.auth.transport.requests
import requests

PROJECT_ID = "qwiklabs-gcp-03-4001ab701a83"

def create_db():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases?databaseId=(default)"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    body = {
        "locationId": "us-central1",
        "type": "FIRESTORE_NATIVE"
    }
    
    response = requests.post(url, json=body, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    create_db()
