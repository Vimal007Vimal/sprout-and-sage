import datetime
from typing import Any, Optional
from google.cloud import firestore

# Hardcoded project ID as required to ensure compatibility with deployed environments
PROJECT_ID = "qwiklabs-gcp-03-4001ab701a83"

def get_db():
    return firestore.Client(project=PROJECT_ID, database="(default)")


def log_watering_event(plant_name: str, notes: str = "") -> str:
    """Logs a plant watering care event with a timestamp into the Firestore database.

    Args:
        plant_name: Common name of the plant watered (e.g. 'Monstera Deliciosa' or 'Snake Plant').
        notes: Optional details about soil moisture, liquid fertilizer added, or care notes.

    Returns:
        A confirmation string with the recorded details.
    """
    try:
        db = get_db()
        now = datetime.datetime.now(datetime.timezone.utc)
        log_data = {
            "plant_name": plant_name,
            "timestamp": now.isoformat(),
            "notes": notes,
        }
        db.collection("care_logs").add(log_data)
        return f"Successfully logged watering event for '{plant_name}' at {now.strftime('%Y-%m-%d %H:%M UTC')}."
    except Exception as e:
        return f"Error logging watering event to Firestore: {e}"


def list_nursery_stock() -> str:
    """Lists all plants currently available in the nursery inventory database.

    Returns:
        A string formatted list of plant items in the collection with their details.
    """
    try:
        db = get_db()
        docs = db.collection("plants").stream()
        plants = [doc.to_dict() for doc in docs]
        if not plants:
            return "No plants found in the nursery inventory."
        
        result = []
        for p in plants:
            result.append(
                f"- ID: {p.get('id', 'N/A')} | Name: {p.get('name', 'N/A')} ({p.get('scientific_name', '')}) "
                f"| Difficulty: {p.get('care_difficulty', 'N/A')} | Light: {p.get('light_requirement', 'N/A')} "
                f"| Water every: {p.get('watering_frequency_days', 'N/A')} days | Price: ${p.get('price', 0.0):.2f}"
            )
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving nursery stock from Firestore: {e}"


def get_plant_info(plant_id_or_name: str) -> str:
    """Retrieves detailed care and inventory information for a specific plant from Firestore.

    Args:
        plant_id_or_name: The ID or common name of the plant (e.g. 'monstera-deliciosa' or 'Monstera Deliciosa').

    Returns:
        A string with the plant details or an error message if not found.
    """
    try:
        db = get_db()
        plants_ref = db.collection("plants")
        
        # 1. Direct document lookup by ID
        doc = plants_ref.document(plant_id_or_name.lower().replace(" ", "-")).get()
        if doc.exists:
            p = doc.to_dict()
            return (
                f"Plant Details for {p.get('name')}:\n"
                f"- ID: {p.get('id')}\n"
                f"- Scientific Name: {p.get('scientific_name')}\n"
                f"- Care Difficulty: {p.get('care_difficulty')}\n"
                f"- Light Requirement: {p.get('light_requirement')}\n"
                f"- Watering Frequency: Every {p.get('watering_frequency_days')} days\n"
                f"- Price: ${p.get('price', 0.0):.2f}\n"
                f"- In Stock: {p.get('in_stock', True)}\n"
                f"- Description: {p.get('description', '')}"
            )
        
        # 2. Query fallback by name
        docs = plants_ref.stream()
        for d in docs:
            p = d.to_dict()
            if plant_id_or_name.lower() in p.get("name", "").lower() or plant_id_or_name.lower() in p.get("id", "").lower():
                return (
                    f"Plant Details for {p.get('name')}:\n"
                    f"- ID: {p.get('id')}\n"
                    f"- Scientific Name: {p.get('scientific_name')}\n"
                    f"- Care Difficulty: {p.get('care_difficulty')}\n"
                    f"- Light Requirement: {p.get('light_requirement')}\n"
                    f"- Watering Frequency: Every {p.get('watering_frequency_days')} days\n"
                    f"- Price: ${p.get('price', 0.0):.2f}\n"
                    f"- In Stock: {p.get('in_stock', True)}\n"
                    f"- Description: {p.get('description', '')}"
                )
        
        return f"Plant '{plant_id_or_name}' not found in nursery database."
    except Exception as e:
        return f"Error retrieving plant info from Firestore: {e}"


def add_or_update_plant(
    plant_id: str,
    name: str,
    scientific_name: str,
    care_difficulty: str,
    light_requirement: str,
    watering_frequency_days: int,
    price: float,
    in_stock: bool = True,
    description: str = "",
) -> str:
    """Adds a new plant or updates an existing plant record in the Firestore nursery database.

    Args:
        plant_id: Unique slug/identifier for the plant (e.g., 'pothos').
        name: Common name of the plant (e.g. 'Golden Pothos').
        scientific_name: Scientific botanical name (e.g. 'Epipremnum aureum').
        care_difficulty: Difficulty rating (e.g. 'Easy', 'Moderate', 'High').
        light_requirement: Light condition needs (e.g. 'Low to Medium Light').
        watering_frequency_days: Recommended interval between waterings in days (e.g. 7).
        price: Retail price in USD (e.g. 18.50).
        in_stock: Whether the item is currently available.
        description: Short description of the plant.

    Returns:
        Confirmation message.
    """
    try:
        db = get_db()
        clean_id = plant_id.lower().strip().replace(" ", "-")
        data = {
            "id": clean_id,
            "name": name,
            "scientific_name": scientific_name,
            "care_difficulty": care_difficulty,
            "light_requirement": light_requirement,
            "watering_frequency_days": int(watering_frequency_days),
            "price": float(price),
            "in_stock": bool(in_stock),
            "description": description,
        }
        db.collection("plants").document(clean_id).set(data)
        return f"Successfully saved plant '{name}' (ID: {clean_id}) in Firestore database."
    except Exception as e:
        return f"Error saving plant to Firestore: {e}"
