# 🏋️‍♂️ Fitness Coach AI

An intelligent, full-stack agentic fitness and nutrition coach built with the Google Agent Development Kit (ADK), Google Cloud Run, Vertex AI Memory Bank, A2A Protocol, and A2UI (Agent-to-User Interface).

![Fitness Coach Live Demo](https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/images/demo.gif)

## 🌟 Features

- **Real Exercise & Workout Discovery**: Queries the free [wger Workout Manager](https://wger.de) REST API to fetch verified exercises, descriptions, and primary muscle targets without hardcoded data.
- **Multimodal Image Generation**: Emits dynamic AI visualizations for customized healthy meals, smoothie bowls, and fitness items using `gemini-3.1-flash-lite-image`. Uploaded automatically to Google Cloud Storage with instant public HTTPS URLs.
- **Demo Video Generation**: Generates workout movement demonstration clips stored in Google Cloud Storage and returned as streaming video resources.
- **Cross-Session Long-Term Memory**: Powered by Vertex AI Memory Bank (`agentengine://6252904485220253696`). Automatically retains user allergies, dietary preferences, and personal fitness constraints across disparate chat sessions using `PreloadMemoryTool` and callback extraction.
- **Rich A2UI Interactive Rendering**: Emits A2UI standard catalog specifications (v0.8) displaying cards, columns, custom headers, and embedded images seamlessly.
- **Serverless Cloud Run Architecture**: Deployed as an authenticated microservices backend running the A2A protocol, paired with a custom branded FastAPI chat frontend.

---

## 🚀 Live Deployments

- **Web Chat Application**: [https://fitness-coach-frontend-122990463099.us-east1.run.app](https://fitness-coach-frontend-122990463099.us-east1.run.app)
- **A2A Agent Engine Service**: [https://fitness-coach-122990463099.us-east1.run.app](https://fitness-coach-122990463099.us-east1.run.app)
- **Demo Video with Lo-Fi Track**: [https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/videos/demo.mp4](https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/videos/demo.mp4)

---

## 🏗️ Architecture & Protocols

```
┌───────────────────────────────┐
│        Web Browser            │
│  (Custom HTML/CSS/JS Chat)    │
└───────────────▲───────────────┘
                │ HTTP (JSON/A2UI cards)
┌───────────────▼───────────────┐
│     FastAPI Web Proxy         │  (Cloud Run: fitness-coach-frontend)
│  (ID Token Auth, A2A Client)  │
└───────────────▲───────────────┘
                │ A2A Protocol (JSON-RPC 2.0)
┌───────────────▼───────────────┐
│     Fitness Coach Agent       │  (Cloud Run: fitness-coach)
│   (ADK Root Agent + Tools)    │
└───────────────▲───────────────┘
        │       │       │
        ▼       ▼       ▼
┌───────────┐ ┌───────────────────┐ ┌──────────────────────┐
│ wger API  │ │ Vertex AI Memory  │ │ Cloud Storage Bucket │
│ Exercises │ │ (Allergies/Prefs) │ │ (Images & Videos)    │
└───────────┘ └───────────────────┘ └──────────────────────┘
```

---

## 🛠️ Tools & Capabilities

### 1. `search_exercises(query, limit)`
Searches the public `wger.de/api/v2/exerciseinfo/` endpoint for real fitness data. Matches workouts with description text and targeted muscle groups.

### 2. `generate_item_image(item_name, tool_context)`
Generates custom fitness meals or workout gear imagery using `gemini-3.1-flash-lite-image`. Saves the artifact in ADK, uploads to `gs://bwg3-qwiklabs-gcp-04-cc6a8d791f03/images/`, and returns the public HTTPS URL for rich A2UI card display.

### 3. `generate_item_video(item_name, tool_context)`
Creates demonstration video assets, persists to Cloud Storage, and returns streaming links.

### 4. `PreloadMemoryTool` & `generate_memories_callback`
Reads and writes user facts to Vertex AI Memory Bank, ensuring user dietary restrictions (e.g., peanut allergies, vegetarian diets) are strictly respected.

---

## 💻 Local Development

### Prerequisites
- Python 3.12+
- `uv` package manager
- `gcloud` authenticated with Vertex AI permissions

### Running the Agent Playground
```bash
cd fitness-coach
uv run adk web --port 8080 --allow_origins "*" --reload_agents --memory_service_uri=agentengine://6252904485220253696
```

### Running the Frontend Locally
```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="https://fitness-coach-122990463099.us-east1.run.app"
export AGENT_DIRECTORY="app"
python main.py
```
Open [http://localhost:8080](http://localhost:8080) to interact with your agent!
