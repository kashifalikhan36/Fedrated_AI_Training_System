from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
action_state = {"action": None}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React frontend build folder
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/build")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/")
def serve_react():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.post("/set_action")
async def set_action(req: Request):
    data = await req.json()
    action_state["action"] = data.get("action")
    return {"status": "ok"}

@app.get("/frontend_action")
def get_action():
    if action_state["action"]:
        return {"action": action_state["action"]}
    return {"action": "waiting"}

@app.post("/skip_task")
def skip_task():
    # Optional: reset or update some state
    action_state["action"] = None
    return {"status": "skipped"}
