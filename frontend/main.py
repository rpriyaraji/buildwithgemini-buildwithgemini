"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.

Why A2A: agents-cli 1.1.0 (GA) deploys ADK agents to Agent Runtime as A2A agents
and no longer registers the reasoning-engine operation schema the old
`agent_engines.get(...).stream_query()` path relied on (operation_schemas() comes
back empty). The container serves the A2A protocol over the Agent Engine HTTP
passthrough, so this proxy fetches the agent's card and sends messages with the
a2a-sdk client (the same path `agents-cli run --mode a2a` uses). This works for
both A2A and plain ADK 1.1.0 deployments (the container serves A2A either way).

Run:
  pip install -r requirements.txt
  export AGENT_ENGINE_RESOURCE_NAME="projects/.../locations/.../reasoningEngines/..."
  export AGENT_DIRECTORY="app"   # your agent's app directory (agents-cli-manifest.yaml)
  python main.py                 # -> http://localhost:8080
"""

import json
import os
import re
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "https://fitness-coach-122990463099.us-east1.run.app")
# The agent's app directory (matches agent_directory in agents-cli-manifest.yaml).
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")

if RESOURCE.startswith("http://") or RESOURCE.startswith("https://"):
    A2A_BASE = f"{RESOURCE.rstrip('/')}/a2a/{AGENT_DIRECTORY}"
else:
    # Location is embedded in the resource name: projects/<p>/locations/<loc>/reasoningEngines/<id>.
    LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]
    A2A_BASE = (
        f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
        f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
    )
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

# The agent tags its A2UI data parts with this mime type.
_A2UI_MIME = "application/json+a2ui"

import google.oauth2.id_token

# Target base URL for ID token generation
_TARGET_AUDIENCE = RESOURCE if RESOURCE.startswith("http") else None

def _auth_headers() -> dict[str, str]:
    auth_req = google.auth.transport.requests.Request()
    if _TARGET_AUDIENCE:
        token = google.oauth2.id_token.fetch_id_token(auth_req, _TARGET_AUDIENCE)
    else:
        _creds.refresh(auth_req)
        token = _creds.token
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    # Always return JSON so the browser never receives a plain-text 500 page
    # (which shows up in the chat as "Unexpected token 'I', "Internal S"... is
    # not valid JSON"). Any server-side failure now surfaces as a readable
    # message in the chat bubble instead.
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


# Reuse ONE A2A context per user so the agent remembers the conversation.
_contexts: dict[str, str] = {}


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    payload = {
        "jsonrpc": "2.0",
        "method": "SendMessage",
        "params": {
            "message": {
                "message_id": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [{"text": message}],
                "context_id": _contexts.get(user_id),
            }
        },
        "id": 1,
    }

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        resp = await client.post(A2A_BASE, json=payload)
        resp_json = resp.json()

        result = resp_json.get("result", {})
        task = result.get("task", {})
        if task.get("contextId"):
            _contexts[user_id] = task["contextId"]

        def _parse_part(p):
            # Check data object first
            data_dict = p.get("data")
            if isinstance(data_dict, dict):
                if "data" in data_dict and data_dict.get("metadata", {}).get("mimeType") == _A2UI_MIME:
                    return [{"kind": "a2ui", "data": data_dict["data"]}]
                elif "surfaceUpdate" in data_dict or "beginRendering" in data_dict:
                    return [{"kind": "a2ui", "data": data_dict}]
            
            # Check text field
            txt = p.get("text", "")
            if isinstance(txt, str) and txt.strip():
                # 1. Check for embedded <a2ui-json> tags
                m = re.search(r"<a2ui-json>(.*?)</a2ui-json>", txt, re.DOTALL)
                if m:
                    intro_text = re.sub(r"<a2ui-json>.*?</a2ui-json>", "", txt, flags=re.DOTALL).strip()
                    extracted_parts = []
                    if intro_text:
                        extracted_parts.append({"kind": "text", "text": intro_text})
                    try:
                        obj = json.loads(m.group(1).strip())
                        if isinstance(obj, dict):
                            if "components" in obj:
                                extracted_parts.append({"kind": "a2ui", "data": {"surfaceUpdate": obj}})
                            elif "surfaceUpdate" in obj or "beginRendering" in obj:
                                extracted_parts.append({"kind": "a2ui", "data": obj})
                    except Exception:
                        pass
                    if extracted_parts:
                        return extracted_parts

                # 2. Check for bare JSON
                cleaned = re.sub(r"</?(?:a2a_datapart_json|a2ui-json)>", "", txt).strip()
                if cleaned.startswith("{") and ("components" in cleaned or "surfaceUpdate" in cleaned or "beginRendering" in cleaned):
                    try:
                        obj = json.loads(cleaned)
                        if isinstance(obj, dict):
                            if "components" in obj:
                                return [{"kind": "a2ui", "data": {"surfaceUpdate": obj}}]
                            elif "surfaceUpdate" in obj or "beginRendering" in obj:
                                return [{"kind": "a2ui", "data": obj}]
                    except Exception:
                        pass
                return [{"kind": "text", "text": txt}]
            return []

        # 1. First check artifacts for rich A2UI or text
        for artifact in task.get("artifacts", []):
            for p in artifact.get("parts", []):
                parsed = _parse_part(p)
                if parsed:
                    parts.extend(parsed)

        # 2. Check history for agent messages
        if not parts:
            for h in task.get("history", []):
                if h.get("role") in ("ROLE_AGENT", "model", "agent"):
                    for p in h.get("parts", []):
                        parsed = _parse_part(p)
                        if parsed:
                            parts.extend(parsed)

        # 3. Direct message in result
        if not parts and "message" in result:
            msg = result["message"]
            for p in msg.get("parts", []):
                parsed = _parse_part(p)
                if parsed:
                    parts.extend(parsed)

    if not parts:
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})


# Serve the chat UI (keep this mount last so /chat wins).
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
