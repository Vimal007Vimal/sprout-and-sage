# Sprout & Sage | Botanical Care & Plant Inventory Assistant

![Sprout & Sage Demo](demo.gif)

**Sprout & Sage** is an intelligent botanical care, plant inventory management, and plant diagnosis assistant built with the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/). It leverages Gemini Flash, Vertex AI Imagen 3, Gemini Omni Flash, Google Cloud Firestore, Google Cloud Storage, and A2UI to deliver visual plant recommendations, care calculations, and stock management.

---

## 🏆 Built for Cognizant "Build with Gemini AI" Event

This project was created as part of the **Build with Gemini AI** hackathon event at **Cognizant**. Co-developed using **Antigravity** (an advanced agentic AI coding assistant built by the **Google DeepMind** team) and powered by Google's **Gemini** foundation models, Antigravity assisted throughout the complete development lifecycle:
- Architecting the Google Agent Development Kit (ADK) multi-tool reasoning pipeline in `app/agent.py`.
- Designing and deploying the custom FastAPI proxy & chat interface with real-time A2UI surface rendering on Cloud Run.
- Integrating Vertex AI Imagen 3 (`imagen-3.0-generate-002`) and Gemini Omni Flash (`gemini-omni-flash-preview`) for multi-modal image and video generation.
- Wiring up persistent Google Cloud Firestore database tools and ADK cross-session memory bank capabilities.

---

## 🌿 Implemented Features & Architecture

Based on the codebase in `app/` and `agents-cli-manifest.yaml`, the agent actively implements the following capabilities:

### 1. Plant Inventory & Nursery Management (Google Cloud Firestore)
- **Database Tools**: `list_nursery_stock`, `get_plant_info`, `add_or_update_plant`, `log_watering_event`.
- **Functionality**: Performs live CRUD operations against Google Cloud Firestore to query nursery stock, check plant care requirements, update stock levels, and log watering events.

### 2. Rich Component Cards (A2UI - Agent-to-User Interface)
- **UI Integration**: Uses `a2ui_callback` and `A2uiSchemaManager` (version 0.8) to construct structured JSON UI component trees (Cards, Columns, Rows, Text, Images).
- **Functionality**: Transformed dynamically by the custom frontend into structured visual cards for plant recommendations, nursery stock tables, and care guidelines.

### 3. AI Image Generation (Vertex AI Imagen 3)
- **Model**: `imagen-3.0-generate-002` via Vertex AI.
- **Functionality**: `generate_plant_image` tool creates high-quality botanical images based on user prompts, uploads the raw image bytes directly to Google Cloud Storage (`sprout-and-sage-assets-...`), and returns a public HTTPS URL.

### 4. AI Video Generation (Vertex AI Gemini Omni Flash)
- **Model**: `gemini-omni-flash-preview` in location `global`.
- **Functionality**: `generate_plant_video` tool generates botanical video demonstrations, saves the video artifact via ADK `tool_context.save_artifact`, uploads video bytes to Google Cloud Storage, and returns a public HTTPS URL.

### 5. Cross-Session Memory Bank (ADK Preload Memory)
- **Memory Integration**: `PreloadMemoryTool` and `generate_memories_callback` (`add_session_to_memory`).
- **Functionality**: Persists and recalls user preferences, plant care history, and health/allergy profiles (e.g., plant sap sensitivities or pollen allergies) across chat sessions.

### 6. Live Weather & Ambient Conditions (Open-Meteo API)
- **Tool**: `get_live_ambient_conditions`.
- **Functionality**: Fetches real-time temperature and humidity data for any city to calculate accurate watering schedules based on current ambient evaporation rates.

### 7. Nearby Garden Center Locator (Google Maps Places & Geocoding)
- **Tools**: `geocode_address` and `find_nearby_places`.
- **Functionality**: Geocodes user locations and finds nearby nurseries, garden centers, or plant shops using Google Maps.

### 8. Python Math & Sandboxed Code Execution
- **Code Executor**: `AgentEngineSandboxCodeExecutor` on Vertex AI Agent Engine.
- **Functionality**: Evaluates mathematical expressions and custom plant watering formulas securely within an isolated Vertex AI sandbox.

---

## 🔮 Planned / Not Yet Implemented

- **RAG Knowledge Base**: Indexing PDF plant manuals via Vertex AI Search (planned for future release; not currently integrated into `app/agent.py`).

---

## 📂 Project Structure

```
sprout-and-sage/
├── app/                        # Core ADK agent application
│   ├── agent.py               # Main agent configuration & tool registration
│   ├── a2ui_utils.py          # A2UI callback and surface rendering helpers
│   ├── firestore_backend.py   # Firestore database tools for nursery stock
│   ├── image_tool.py          # Imagen 3 image generation & GCS upload tool
│   ├── video_tool.py          # Gemini Omni Flash video generation tool
│   ├── maps_tools.py          # Google Maps geocoding & places tools
│   └── fast_api_app.py        # Backend FastAPI server
├── frontend/                  # Custom chat UI & proxy server
│   ├── main.py                # FastAPI frontend proxy
│   ├── static/index.html      # Responsive chat interface with A2UI renderer
│   └── Dockerfile             # Frontend Cloud Run Dockerfile
├── agents-cli-manifest.yaml   # Manifest for agents-cli deployment
├── demo.gif                   # Looping demonstration recording
├── record_demo.py             # Playwright recording script
└── pyproject.toml             # Python dependencies
```

---

## 🚀 Local Setup & Running Instructions

### Prerequisites
- **Python**: 3.11+
- **uv**: Fast Python package manager
- **Google Cloud SDK**: Authenticated with `gcloud auth application-default login`

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Environment Variables

Set your GCP project and resource configuration in your environment or `.env` file:

```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export FIRESTORE_PROJECT_ID="<your-gcp-project-id>"
export GCS_BUCKET_NAME="<your-gcs-bucket-name>"
```

### 3. Run Backend Agent Locally

Start the backend agent using `agents-cli`:

```bash
uv run agents-cli dev
```

Alternatively, run the local playground:

```bash
uv run agents-cli playground
```

### 4. Run Frontend Locally

In a separate terminal, start the custom chat UI:

```bash
cd frontend
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Then open your browser to `localhost:8080` to interact with Sprout & Sage.
