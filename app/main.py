import asyncio
import hashlib
import os
import json
import random
import string
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="WebSocket vs REST PoC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def heavy_mix(seed: str, rounds: int) -> str:
    data = seed.encode()
    for i in range(rounds):
        data = hashlib.sha256(data + i.to_bytes(2, "little")).digest()
    return data.hex()


def generate_payload_bytes(target_size: int = 12 * 1024, work_factor: int = 32) -> str:
    chunk_source = (string.ascii_letters + string.digits) * 50
    out = []
    total = 0
    while total < target_size:
        seed = "".join(random.sample(chunk_source, k=32))
        block = heavy_mix(seed, work_factor)
        out.append(block)
        total += len(block)
    random.shuffle(out)
    payload = "".join(out)
    return payload[:target_size]


def add_serde_rounds(message: dict, serde_rounds: int) -> dict:
    result = message
    for _ in range(max(0, serde_rounds)):
        result = json.loads(json.dumps(result))
    return result


@app.post("/rest-feed")
async def rest_feed(size: int = 20 * 1024, work: int = 32, serde: int = 0) -> JSONResponse:
    payload = generate_payload_bytes(size, work_factor=work)
    message = {"ts": time.time(), "size": len(payload), "payload": payload}
    message = add_serde_rounds(message, serde_rounds=serde)
    return JSONResponse(content=message)


@app.websocket("/ws-feed")
async def websocket_feed(websocket: WebSocket):
    await websocket.accept()
    query_params = websocket.query_params
    target_size = int(query_params.get("size", 20 * 1024))
    interval = float(query_params.get("interval", 5))
    work_factor = int(query_params.get("work", 32))
    serde_rounds = int(query_params.get("serde", 0))

    try:
        while True:
            payload = generate_payload_bytes(target_size, work_factor=work_factor)
            message = {"ts": time.time(), "size": len(payload), "payload": payload}
            message = add_serde_rounds(message, serde_rounds=serde_rounds)
            await websocket.send_json(message)
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        # Client closed the connection; exit cleanly.
        return
    except Exception:
        # Avoid crashing the server because of a single connection.
        await websocket.close()
        raise


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
