import asyncio
from fastapi import FastAPI, HTTPException
from z407 import Z407Remote

app = FastAPI()
z407_remote = None

@app.on_event("startup")
async def startup_event():
    global z407_remote
    async for device in Z407Remote.devices():
        z407_remote = Z407Remote(device.address)
        await z407_remote.connect()
        break
    if not z407_remote:
        raise RuntimeError("Z407 not found.")

@app.on_event("shutdown")
async def shutdown_event():
    if z407_remote:
        await z407_remote.disconnect()

@app.get("/status")
async def status():
    if z407_remote and z407_remote.client.is_connected:
        return {"status": "connected"}
    return {"status": "disconnected"}

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
