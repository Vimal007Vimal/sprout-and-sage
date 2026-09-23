# Seed script for Firestore plant nursery database
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-4001ab701a83"

def seed_database():
    db = firestore.Client(project=PROJECT_ID, database="(default)")
    plants_ref = db.collection("plants")

    seed_items = [
        {
            "id": "monstera-deliciosa",
            "name": "Monstera Deliciosa",
            "scientific_name": "Monstera deliciosa",
            "care_difficulty": "Easy",
            "light_requirement": "Bright Indirect Light",
            "watering_frequency_days": 7,
            "price": 29.99,
            "in_stock": True,
            "description": "Popular tropical plant known for its iconic natural split leaves (fenestrations).",
        },
        {
            "id": "snake-plant",
            "name": "Snake Plant (Sansevieria)",
            "scientific_name": "Dracaena trifasciata",
            "care_difficulty": "Easy",
            "light_requirement": "Low to Bright Indirect Light",
            "watering_frequency_days": 14,
            "price": 19.99,
            "in_stock": True,
            "description": "Extremely resilient architectural indoor plant that tolerates low light and neglect.",
        },
        {
            "id": "peace-lily",
            "name": "Peace Lily",
            "scientific_name": "Spathiphyllum",
            "care_difficulty": "Moderate",
            "light_requirement": "Medium to Low Light",
            "watering_frequency_days": 5,
            "price": 24.99,
            "in_stock": True,
            "description": "Lush indoor plant with glossy green leaves and elegant white flowering spathes.",
        },
        {
            "id": "fiddle-leaf-fig",
            "name": "Fiddle-Leaf Fig",
            "scientific_name": "Ficus lyrata",
            "care_difficulty": "High",
            "light_requirement": "Bright Direct to Indirect Light",
            "watering_frequency_days": 7,
            "price": 49.99,
            "in_stock": True,
            "description": "Stunning focal plant with large violin-shaped glossy leaves. Prefers consistent light.",
        },
    ]

    for item in seed_items:
        doc_id = item["id"]
        plants_ref.document(doc_id).set(item)
        print(f"Seeded plant document: {doc_id}")

    print("Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
