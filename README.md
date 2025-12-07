# websocket_vs_rest

POC: compare REST polling vs WebSocket push for a frontend that needs a ~20KB update every 5 seconds. Implemented with FastAPI.

## Quickstart
1) Install deps:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2) Run the server:
```
python -m app.main
```
3) Open the demo page:
   - `frontend/index.html` in your browser (static file). Update the host fields if your server runs elsewhere.

## Monitoring CPU/Memory
- Find PID: `Get-Process -Name python | Sort-Object StartTime | Select -Last 1 | Select -ExpandProperty Id`
- Run sampler (JSON lines): `python monitor.py <pid> --interval 2 --samples 60 > rest.jsonl`
- Repeat for WebSocket mode to compare averages.

## Endpoints
- REST (poll every 5s): `POST http://localhost:8000/rest-feed?size=20000&work=32&serde=0`
- WebSocket (server pushes every 5s): `ws://localhost:8000/ws-feed?size=20000&interval=5&work=32&serde=0`
  - Adjust `size` (bytes), `interval` (seconds), `work` (hash rounds per block), and `serde` (JSON serialize/deserialize loops) via query params.

Each payload contains `{ ts, size, payload }` where `payload` is a synthetic ASCII blob sized to your request.

## How to test your use case
- REST: poll `/rest-feed` every 5 seconds from the frontend; observe size/latency.
- WebSocket: open `/ws-feed` once and listen for messages; note bandwidth and CPU usage.
- Capture client-perceived latency (time between request and response or between pushes) and process memory/CPU to compare behaviors. Use browser devtools network panel or a small script.
