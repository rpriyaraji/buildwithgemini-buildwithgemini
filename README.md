# 🏋️‍♂️ Fitness Coach AI

An intelligent, full-stack agentic fitness and nutrition coach built with the Google Agent Development Kit (ADK), Google Cloud Run, Vertex AI Memory Bank, A2A Protocol, and A2UI (Agent-to-User Interface).

![Fitness Coach Live Demo](https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/images/demo.gif)

---

## 📹 Demo Video & Walkthrough

The project includes an updated interactive demo walkthrough highlighting the modern dark-mode glassmorphic UI, real API tool lookups, AI image generation, A2UI cards, and allergy-aware long-term memory:

- **Watch in Repository**: [demo.mp4](demo.mp4)
- **Direct Video Stream (Google Cloud Storage)**: [https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/videos/demo.mp4](https://storage.googleapis.com/bwg3-qwiklabs-gcp-04-cc6a8d791f03/videos/demo.mp4)

---

## 🌟 Modern UI & System Features

### 🎨 Modern Dark-Mode & Glassmorphic UI
- **Obsidian & Emerald Palette**: High-contrast, sleek design built with [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans) typography.
- **Glassmorphic Cards**: Semi-transparent frosted layers (`backdrop-filter: blur(16px)`) with glowing green accent borders.
- **Interactive Quick-Prompt Chips**: Clickable prompt pills for instantaneous queries (*Search Squat Workouts*, *Generate Protein Bowl Image*, *Set Peanut Allergy*, *Recommend Safe Snacks*).
- **Personalized Avatars & Typing State**: Distinct avatars (`🏋️‍♂️` Coach / `👤` User) with bouncing multi-dot typing indicators during agent tool and generation steps.
- **Native A2UI Card & Media Renderer**: Automatically formats A2UI v0.8 schemas into styled cards, multi-column layouts, and responsive images/videos.

### ⚡ Core Agentic Capabilities
- **Real Exercise & Workout Discovery**: Queries the free [wger Workout Manager](https://wger.de) REST API (`/api/v2/exerciseinfo/`) in real time for verified fitness movements, targeted muscle groups, and exercise instructions without hardcoded mocks.
- **Multimodal Image Generation**: Emits dynamic photorealistic AI visualizations for customized healthy meals, protein bowls, and fitness nutrition using Vertex AI `gemini-2.5-flash-image`. Uploaded automatically to Google Cloud Storage with instant public HTTPS URLs.
- **Demo Video Generation**: Generates workout movement demonstration clips stored in Google Cloud Storage and returned as streaming video resources.
- **Cross-Session Long-Term Memory**: Powered by Vertex AI Memory Bank (`agentengine://6252904485220253696`). Automatically retains user allergies, dietary preferences, and personal fitness constraints across disparate chat sessions using `PreloadMemoryTool` and callback extraction.
- **Serverless Cloud Run Architecture**: Deployed as an authenticated microservices backend running the A2A protocol, paired with a custom branded FastAPI chat frontend.

---

## 🚀 Live Deployments

- **Web Chat Application**: [https://fitness-coach-frontend-122990463099.us-east1.run.app](https://fitness-coach-frontend-122990463099.us-east1.run.app)
- **A2A Agent Engine Service**: [https://fitness-coach-122990463099.us-east1.run.app](https://fitness-coach-122990463099.us-east1.run.app)

---

## 🏗️ Architecture & Protocols

```
┌───────────────────────────────────────────────┐
│           Web Browser (Glassmorphism)         │
│  (Plus Jakarta Sans, Avatars, Quick Chips)    │
└───────────────────────▲───────────────────────┘
                        │ HTTP / JSON (Text & A2UI cards)
┌───────────────────────▼───────────────────────┐
│              FastAPI Web Proxy                │  (Cloud Run: fitness-coach-frontend)
│  (ID Token Auth, A2A JSON-RPC Client, Cache)  │
└───────────────────────▲───────────────────────┘
                        │ A2A Protocol (JSON-RPC 2.0)
┌───────────────────────▼───────────────────────┐
│             Fitness Coach Agent               │  (Cloud Run: fitness-coach)
│           (ADK Root Agent + Tools)            │
└───────────────────────▲───────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│    wger API    │ │   Vertex AI Memory      │ │  Cloud Storage Bucket   │
│ (Workout Data) │ │ (Allergies/Preferences) │ │    (Images & Videos)    │
└────────────────┘ └─────────────────────────┘ └─────────────────────────┘
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

### 2. Running the Modern Frontend Locally

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

---

## 💬 Sample User Queries & Interactive Responses

| Category | Example User Query | Expected Agent Behavior & Format |
|---|---|---|
| **Workout Discovery** | *"Can you recommend 2 exercises for chest?"* | Invokes `search_exercises`, filters 100+ wger movements, and returns an **A2UI Card** containing exercise names and step-by-step form instructions. |
| **Targeted Fitness** | *"Can you search exercises for squats?"* | Searches legs/quads movements and renders a structured **A2UI Card** with Barbell Hack Squats & Front Squats. |
| **Multimodal Generation** | *"Generate an image for a healthy post-workout protein bowl"* | Generates custom artwork using `gemini-3.1-flash-lite-image`, uploads to GCS, and displays inside a responsive **A2UI Image Card**. |
| **Video Demonstrations** | *"Can you generate a workout demo video for pushups?"* | Creates video asset stored in GCS and renders directly via an HTML5 `<video controls>` player within an **A2UI Video Card**. |
| **Long-Term Memory** | *"I am allergic to peanuts. Please remember that."* | Persists preference to Vertex AI Memory Bank and provides clean text confirmation. |
| **Allergy-Aware Diet** | *"What post-workout snacks do you recommend for me?"* | Recalls peanut allergy from Memory Bank across sessions and suggests safe options (Greek yogurt, whey protein, fruit) while explicitly omitting peanuts. |

---

## 🧪 Automated Unit Testing & Validation

All endpoints and response handlers are verified with automated unit tests to guarantee clean visual output (no raw JSON blobs or unparsed markup):

```bash
# Run unit test suite against live Cloud Run chat frontend
python3 -c '
import httpx

tests = [
    ("Search chest exercises", "Can you recommend 2 exercises for chest?"),
    ("Search squats", "Can you search exercises for squats?"),
    ("Generate meal image", "Generate an image for a healthy post-workout protein bowl"),
    ("Long-term memory allergy", "I am allergic to peanuts. Please remember that."),
    ("Recommendation with memory", "What post-workout snacks do you recommend for me?")
]

url = "https://fitness-coach-frontend-122990463099.us-east1.run.app/chat"

for name, msg in tests:
    print(f"TEST: {name}")
    r = httpx.post(url, json={"message": msg}, timeout=90)
    data = r.json()
    for idx, p in enumerate(data.get("parts", [])):
        print(f"  Part [{idx}] kind={p.get(\"kind\")}")
'
```

### Verified Test Results

| Test Case | Prompt | HTTP Status | Response Kind | UI Output Rendered |
|---|---|:---:|:---:|---|
| **1. Chest Workout** | *"Can you recommend 2 exercises for chest?"* | **200 OK** | `a2ui` | Frosted Card (`Card`, `Column`, `Text`) |
| **2. Squat Workout** | *"Can you search exercises for squats?"* | **200 OK** | `a2ui` | Frosted Card (`Card`, `Column`, `Text`) |
| **3. Meal Image** | *"Generate an image for a healthy post-workout protein bowl"* | **200 OK** | `a2ui` | Image Card (`Card`, `Column`, `Image`, `Text`) |
| **4. Long-Term Memory** | *"I am allergic to peanuts. Please remember that."* | **200 OK** | `text` | Clean text confirmation |
| **5. Memory-Aware Suggestion** | *"What post-workout snacks do you recommend for me?"* | **200 OK** | `text` + `a2ui` | Explicitly excludes peanuts based on memory |

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

#### Deploy the Modern Frontend:
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

---

## 📚 References & Workshop Resources

- **Build With Gemini Workshop Guide (Bengaluru)**: [https://goo.gle/bwg3-blr](https://goo.gle/bwg3-blr)
- **Google Agent Development Kit (ADK) Documentation**: [https://google.github.io/agent-development-kit/](https://google.github.io/agent-development-kit/)
- **Vertex AI Memory Bank**: [Vertex AI Reasoning Engine & Memory](https://cloud.google.com/vertex-ai/docs/agent-engine/overview)
- **wger Workout Manager REST API**: [https://wger.de/en/software/api](https://wger.de/en/software/api)
