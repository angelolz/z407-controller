import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from z407 import Z407Remote
from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
SERVICE_UUID = "0000fdc2-0000-1000-8000-00805f9b34fb"

class NoGetLogging(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not (record.levelname == "INFO" and ("GET / " in message or "GET /status " in message))

logging.getLogger("uvicorn.access").addFilter(NoGetLogging())

app = FastAPI()
z407_remote = None

@app.on_event("startup")
async def startup_event():
    global z407_remote
    max_attempts = 5
    attempt = 0
    device = None

    while attempt < max_attempts and device is None:
        print(f"Attempt {attempt + 1} to find Z407...")
        try:
            device = await BleakScanner.find_device_by_filter(
                lambda d, ad: SERVICE_UUID in ad.service_uuids,
                timeout=10.0
            )
        except Exception as e:
            print(f"Error during scanning: {e}")

        if device:
            print(f"Found device {device.name} ({device.address})")
            global z407_remote
            z407_remote = Z407Remote(device.address)
            try:
                await z407_remote.connect()
                print(f"Connected to Z407 on attempt {attempt + 1}")
                return  # Success!
            except Exception as e:
                print(f"Failed to connect on attempt {attempt + 1}: {e}")
                device = None  # Reset device to allow re-scanning
        
        attempt += 1
        if not device:
            await asyncio.sleep(2) # Cooldown

    if not z407_remote or not z407_remote.client.is_connected:
        raise RuntimeError("Failed to connect to Z407 after multiple attempts.")

@app.on_event("shutdown")
async def shutdown_event():
    if z407_remote:
        await z407_remote.disconnect()

@app.get("/status")
async def status():
    if z407_remote and z407_remote.client.is_connected:
        return {"status": "connected", "connection_mode": z407_remote.connection_mode, "bluetooth_status": z407_remote.bluetooth_status}
    return {"status": "disconnected", "connection_mode": "disconnected", "bluetooth_status": "unknown"}

@app.post("/volume-up")
async def volume_up():
    try:
        await z407_remote.volume_up()
        return {"status": "volume up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/volume-down")
async def volume_down():
    try:
        await z407_remote.volume_down()
        return {"status": "volume down"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/play-pause")
async def play_pause():
    try:
        await z407_remote.play_pause()
        return {"status": "toggled play/pause"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input-bluetooth")
async def input_bluetooth():
    try:
        await z407_remote.input_bluetooth()
        return {"status": "switched to bluetooth"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input-aux")
async def input_aux():
    try:
        await z407_remote.input_aux()
        return {"status": "switched to aux"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input-usb")
async def input_usb():
    try:
        await z407_remote.input_usb()
        return {"status": "switched to usb"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bt-pair")
async def pair():
    try:
        await z407_remote.bluetooth_pair()
        return {"status": "pairing for new device"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset():
    try:
        await z407_remote.factory_reset()
        return {"status": "reset device"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
