"""
Virtual UART N-P-K Sensor Listener
Provides a WebSocket endpoint that accepts real-time sensor frames.
Also includes a simulation generator for testing without hardware.
"""
import asyncio
import json
import random
import time
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

# In-memory store for latest sensor readings
_latest_reading: dict = {}
_connected_clients: Set[WebSocket] = set()


def get_latest_reading() -> dict:
    return _latest_reading.copy()


def _parse_uart_frame(raw: str) -> dict | None:
    """
    Parse a UART sensor frame.
    Accepted formats:
      JSON: {"N":35.2,"P":28.1,"K":42.5,"pH":6.4,"moisture":55.0}
      CSV:  35.2,28.1,42.5,6.4,55.0   (N,P,K,pH,moisture)
    """
    raw = raw.strip()
    try:
        data = json.loads(raw)
        return {
            "N": float(data.get("N", data.get("n", 35.0))),
            "P": float(data.get("P", data.get("p", 28.0))),
            "K": float(data.get("K", data.get("k", 40.0))),
            "pH": float(data.get("pH", data.get("ph", 6.5))),
            "moisture": float(data.get("moisture", data.get("moist", 50.0))),
            "timestamp": time.time(),
            "source": "uart_json"
        }
    except (json.JSONDecodeError, ValueError):
        pass
    # Try CSV
    try:
        parts = [float(x.strip()) for x in raw.split(",")]
        if len(parts) >= 3:
            return {
                "N": parts[0], "P": parts[1], "K": parts[2],
                "pH": parts[3] if len(parts) > 3 else 6.5,
                "moisture": parts[4] if len(parts) > 4 else 50.0,
                "timestamp": time.time(),
                "source": "uart_csv"
            }
    except ValueError:
        pass
    return None


async def uart_websocket_handler(websocket: WebSocket):
    """WebSocket handler for real-time N-P-K sensor data."""
    global _latest_reading
    await websocket.accept()
    _connected_clients.add(websocket)
    try:
        await websocket.send_json({
            "status": "connected",
            "message": "UART listener ready. Send JSON or CSV frames.",
            "format": '{"N":35.2,"P":28.1,"K":42.5,"pH":6.4,"moisture":55.0}'
        })
        while True:
            raw = await websocket.receive_text()
            parsed = _parse_uart_frame(raw)
            if parsed:
                _latest_reading = parsed
                # Broadcast to all connected clients
                dead = set()
                for client in _connected_clients:
                    try:
                        await client.send_json({
                            "type": "sensor_update",
                            "data": parsed
                        })
                    except Exception:
                        dead.add(client)
                _connected_clients -= dead
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Could not parse frame: {raw[:80]}"
                })
    except WebSocketDisconnect:
        pass
    finally:
        _connected_clients.discard(websocket)


async def simulate_sensor_stream(websocket: WebSocket):
    """Generates synthetic N-P-K readings for demo/testing."""
    global _latest_reading
    await websocket.accept()
    _connected_clients.add(websocket)
    try:
        base_n, base_p, base_k = 35.0, 28.0, 40.0
        tick = 0
        while True:
            # Simulate gradual nutrient depletion with noise
            noise = lambda: random.gauss(0, 1.5)
            reading = {
                "N": round(max(5, base_n - tick * 0.1 + noise()), 2),
                "P": round(max(3, base_p - tick * 0.05 + noise()), 2),
                "K": round(max(5, base_k - tick * 0.08 + noise()), 2),
                "pH": round(6.5 + random.gauss(0, 0.1), 2),
                "moisture": round(50.0 + random.gauss(0, 5.0), 1),
                "timestamp": time.time(),
                "source": "virtual_uart_sim",
                "tick": tick
            }
            _latest_reading = reading
            await websocket.send_json({"type": "sensor_update", "data": reading})
            tick += 1
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        pass
    finally:
        _connected_clients.discard(websocket)
