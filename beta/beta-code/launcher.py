import subprocess
import time
import requests
import os
import sys

def start_fastapi():
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "5000"])

def wait_for_action():
    while True:
        try:
            response = requests.get("http://127.0.0.1:5000/frontend_action")
            if response.status_code == 200:
                action = response.json().get("action")
                if action in ["start", "skip"]:
                    return action
        except:
            pass
        time.sleep(1)

def run_client():
    subprocess.call([sys.executable, "client.py"])

if __name__ == "__main__":
    print("[Launcher] Starting FastAPI server...")
    api_proc = start_fastapi()
    time.sleep(3)  # Give it time to start

    # Open React app in browser
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")

    try:
        action = wait_for_action()

        if action == "start":
            print("[Launcher] User selected: Start Task")
            run_client()
        elif action == "skip":
            print("[Launcher] User selected: Skip Task")
            requests.post("http://127.0.0.1:5000/skip_task")
    finally:
        print("[Launcher] Shutting down FastAPI server...")
        api_proc.terminate()
