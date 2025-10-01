import asyncio
from fastapi import FastAPI, HTTPException
from z407 import Z407Remote
from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
SERVICE_UUID = "0000fdc2-0000-1000-8000-00805f9b34fb"

app = FastAPI()
z407_remote = None

@app.on_event("startup")
async def startup_event():
    global z407_remote
    max_attempts = 5
    attempt = 0

    # Create a single scanner outside the loop
    scanner = AsyncBleakScanner(service_uuids=[SERVICE_UUID])

    await scanner.start()
    try:
        while attempt < max_attempts:
            try:
                print(f"Attempt {attempt + 1} to find Z407...")

                try:
                    device = await asyncio.wait_for(scanner._device_queue.get(), timeout=10)
                except asyncio.TimeoutError:
                    device = None

                if device:
                    print(f"Found device {device.name} ({device.address})")
                    z407_remote = Z407Remote(device.address)
                    await z407_remote.connect()
                    print(f"Connected to Z407 on attempt {attempt + 1}")
                    return  # success!

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")

            attempt += 1
            await asyncio.sleep(2)  # Short cooldown between attempts

    finally:
        await scanner.stop()

    raise RuntimeError("Failed to connect to Z407 after multiple attempts.")

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

@app.post("/bt-pair")
async def pair():
    try:
        await z407_remote.bluetoth_pair()
        return {"status": "pairing for new device"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset():
    try:
        await z407_remote.reset()
        return {"status": "reset device"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AsyncBleakScanner(BleakScanner):
    _device_queue: asyncio.Queue

    def __init__(self, **kwargs):
        super().__init__(self._device_found, **kwargs)
        self._device_queue = asyncio.Queue()

    async def _device_found(self, device, advertisement_data):
        await self._device_queue.put(device)

    async def async_discover(self, timeout=60):
        discovered_devices = set()
        await self.start()
        try:
            async with asyncio.timeout(timeout):
                while True:
                    try:
                        # Timeout 5 seconds waiting for a device each time
                        device = await asyncio.wait_for(self._device_queue.get(), timeout=5)
                        if device.address not in discovered_devices:
                            discovered_devices.add(device.address)
                            yield device
                    except asyncio.TimeoutError:
                        # No device found in 5 seconds — keep looping until overall timeout
                        pass
        except TimeoutError:
            pass
        finally:
            await self.stop()