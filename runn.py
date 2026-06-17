import webbrowser
import subprocess
import time
import threading

def open_browser():
    time.sleep(2)  # Wait for server to start
    webbrowser.open("http://127.0.0.1:8000/docs")  # Open Swagger UI

# Start server in background
threading.Thread(target=open_browser).start()
subprocess.run(["uvicorn", "main:app", "--reload"])