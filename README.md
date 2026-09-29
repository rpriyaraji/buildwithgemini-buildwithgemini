# 🏋️‍♂️ Fitness Coach AI

An intelligent, full-stack agentic fitness and nutrition coach built with the Google Agent Development Kit (ADK), Google Cloud Run, Vertex AI Memory Bank, A2A Protocol, and A2UI (Agent-to-User Interface).

![Fitness Coach Live Demo](https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/images/demo.gif)

---

## 📹 Demo Video

The project includes a complete demo walkthrough video with an upbeat lo-fi soundtrack demonstrating real API discovery, image generation, A2UI cards, and allergy-aware memory:

- **Watch on GitHub**: [demo.mp4](demo.mp4)
- **Direct Video Stream (Cloud Storage)**: [https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/videos/demo.mp4](https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/videos/demo.mp4)

---

## 🌟 Features

- **Real Exercise & Workout Discovery**: Queries the free [wger Workout Manager](https://wger.de) REST API (`/api/v2/exerciseinfo/`) to fetch verified exercises, form descriptions, and targeted muscles in real time.
- **Multimodal Image Generation**: Emits dynamic AI visualizations for customized healthy meals, smoothie bowls, and fitness items using `gemini-3.1-flash-lite-image`. Uploaded automatically to Google Cloud Storage with instant public HTTPS URLs.
- **Demo Video Generation**: Generates workout movement demonstration clips stored in Google Cloud Storage and returned as streaming video resources.
- **Cross-Session Long-Term Memory**: Powered by Vertex AI Memory Bank (`agentengine://6252904485220253696`). Automatically retains user allergies, dietary preferences, and personal fitness constraints across disparate chat sessions using `PreloadMemoryTool` and callback extraction.
- **Rich A2UI Interactive Rendering**: Emits A2UI standard catalog specifications (v0.8) displaying cards, columns, custom headers, and embedded images seamlessly.
- **Serverless Cloud Run Architecture**: Deployed as an authenticated microservices backend running the A2A protocol, paired with a custom branded FastAPI chat frontend.

---

## 🚀 Live Deployments

- **Web Chat Application**: [https://fitness-coach-frontend-122990463099.us-east1.run.app](https://fitness-coach-frontend-122990463099.us-east1.run.app)
- **A2A Agent Engine Service**: [https://fitness-coach-122990463099.us-east1.run.app](https://fitness-coach-122990463099.us-east1.run.app)

---

## 🏗️ Architecture & Protocols

```
┌─────────────────────────────────┐
│          Web Browser            │
│   (Custom HTML/CSS/JS Chat)     │
└────────────────▲────────────────┘
                 │ HTTP (JSON/A2UI cards)
┌────────────────▼────────────────┐
│       FastAPI Web Proxy         │  (Cloud Run: fitness-coach-frontend)
│   (ID Token Auth, A2A Client)   │
└────────────────▲────────────────┘
                 │ A2A Protocol (JSON-RPC 2.0)
┌────────────────▼────────────────┐
│      Fitness Coach Agent        │  (Cloud Run: fitness-coach)
│    (ADK Root Agent + Tools)     │
└────────────────▲────────────────┘
         │       │        │
         ▼       ▼        ▼
┌────────────┐ ┌────────────────────┐ ┌───────────────────────┐
│  wger API  │ │ Vertex AI Memory   │ │ Cloud Storage Bucket  │
│  Exercises │ │ (Allergies/Prefs)  │ │ (Images & Videos)     │
└────────────┘ └────────────────────┘ └───────────────────────┘
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
Reads and writes user facts to Vertex AI Memory Bank, ensuring user dietary restrictions (e.g., peanut allergies, vegetarian diets) are strictly respected across different conversations.

---

## 💻 Setup & Execution Guide

### Prerequisites
1. **Python 3.12+** and **uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Google Cloud SDK (`gcloud`)**:
   Authenticate your GCP account and set the active project:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

---

### 1. Running the Agent Playground (Local ADK Web)

To test the agent locally with the interactive ADK Playground and long-term memory:
```bash
cd fitness-coach
uv sync
uv run adk web --port 8080 --allow_origins "*" --reload_agents --memory_service_uri=agentengine://6252904485220253696
```
Open [http://localhost:8080](http://localhost:8080) to interact with the agent tools and view memories.

---

### 2. Running the Frontend Locally

The frontend proxy communicates with the deployed Cloud Run agent over A2A and renders A2UI cards natively:
```bash
cd frontend
pip install -r requirements.txt

export AGENT_ENGINE_RESOURCE_NAME="https://fitness-coach-122990463099.us-east1.run.app"
export AGENT_DIRECTORY="app"
python main.py
```
Open [http://localhost:8080](http://localhost:8080) in your browser.

---

### 3. CLI Testing via `agents-cli`

You can run prompts directly against the deployed Cloud Run A2A service from the terminal:
```bash
# General inquiry
agents-cli run --url https://fitness-coach-122990463099.us-east1.run.app --mode a2a "Hello, who are you?"

# Search exercises
agents-cli run --url https://fitness-coach-122990463099.us-east1.run.app --mode a2a "Recommend 2 leg exercises"

# Generate meal image
agents-cli run --url https://fitness-coach-122990463099.us-east1.run.app --mode a2a "Generate an image for a healthy post-workout protein bowl"
```

---

### 4. Deploying to Cloud Run

#### Deploy the Agent:
```bash
cd fitness-coach
agents-cli deploy --deployment-target cloud_run --memory 2Gi --max-instances 5 --no-confirm-project
```

#### Deploy the Frontend:
```bash
cd frontend
gcloud run deploy fitness-coach-frontend \
  --project YOUR_PROJECT_ID \
  --region us-east1 \
  --source . \
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars "AGENT_ENGINE_RESOURCE_NAME=https://fitness-coach-122990463099.us-east1.run.app,AGENT_DIRECTORY=app"
```

#### Grant Cloud Run Service Account Permissions:
Ensure your Cloud Run runtime service account has the necessary IAM permissions:
```bash
PROJECT_NUM=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"

# Firestore & Vertex AI
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="serviceAccount:${SA}" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="serviceAccount:${SA}" --role="roles/aiplatform.user"

# Cloud Storage for image/video artifacts
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME --member="serviceAccount:${SA}" --role="roles/storage.objectAdmin"
```
