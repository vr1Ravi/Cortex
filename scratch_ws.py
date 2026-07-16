from fastapi.testclient import TestClient
from app.main import app


with TestClient(app).websocket_connect("/demo/ws/echo") as ws:
    for m in ["hello", "cortex", "bye"]:
        ws.send_text(m)
        print(f"sent {m!r} -> got {ws.receive_text()!r}")