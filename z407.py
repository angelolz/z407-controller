import asyncio
from datetime import datetime

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic

SERVICE_UUID = "0000fdc2-0000-1000-8000-00805f9b34fb"
COMMAND_UUID = "c2e758b9-0e78-41e0-b0cb-98a593193fc5"
RESPONSE_UUID = "b84ac9c6-29c5-46d4-bba1-9d534784330f"

class Z407Remote:
    def __init__(self, address: str):
        self.address = address
        self.client = BleakClient(address)
        self.connection_mode = "disconnected"
        self.bluetooth_status = "unknown"
        self.connected = False

    async def connect(self):
        await self.client.connect()

        await self.client.start_notify(RESPONSE_UUID, self._receive_data)
        await self._send_command("8405")

    async def disconnect(self):
        await self.client.disconnect()

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def _receive_data(self, sender: BleakGATTCharacteristic, data: bytearray):
        # todo, describe commands
        match data:
            # initial connection events
            case b"\xd4\x05\x01":
                print("initial connection...")
                await self._send_command("8400")
            case b'\xcf\x0b':
                print("connecting...")

            # connected events
            case b"\xd4\x00\x01":
                print("connected! mode: bluetooth")
                self.connected = True
                self.connection_mode = "bluetooth"
            case b"\xd4\x00\x02":
                print("connected! mode: aux")
                self.connected = True
                self.connection_mode = "aux"
            case b"\xd4\x00\x03":
                print("connected! mode: usb")
                self.connected = True
                self.connection_mode = "usb"

            # volume control events
            case b"\xc0\x02":
                print("received volume up")
            case b"\xc0\x03":
                print("received volume down")
            case b"\xc0\x04":
                print("received play/pause")

            # changing connection modes
            case b'\xc1\x01':
                if self.connection_mode == "bluetooth":
                    print("speakers are already set to bluetooth.")
                else:
                    print("switching to bluetooth...")
            case b'\xc1\x02':
                if self.connection_mode == "aux":
                    print("speakers are already set to aux.")
                else:
                    print("switching to aux...")
            case b'\xc1\x03':
                if self.connection_mode == "usb":
                    print("speakers are already set to usb.")
                else:
                    print("switching to usb...")

            # device changing events
            case b'\xcf\x00':
                self.bluetooth_status = "connected"
                print("paired with a device")
            case b'\xcf\x01':
                self.bluetooth_status = "disconnected"
                print("lost connection with bluetooth device")
            case b'\xc2\x00':
                self.bluetooth_status = "pairing"
                print("set to pairing mode")
            case b'\xcf\x04':
                self.connection_mode = "bluetooth"
                print("switched to bluetooth")
            case b'\xcf\x05':
                self.connection_mode = "aux"
                print("switched to aux.")
            case b'\xcf\x06':
                self.connection_mode = "usb"
                print("switched to usb.")
            case b'\xc3\x00':
                self.bluetooth_status = "disconnected";
                print("device has been reset.")
            case _:
                print("unknown command: {}".format(bytes(data)))

    async def _send_command(self, command):
        await self.client.write_gatt_char(COMMAND_UUID, bytes.fromhex(command), response=False)

    async def volume_up(self):
        await self._send_command("8002")

    async def volume_down(self):
        await self._send_command("8003")

    async def play_pause(self):
        await self._send_command("8004")

    async def input_bluetooth(self):
        await self._send_command("8101")

    async def input_aux(self):
        await self._send_command("8102")

    async def input_usb(self):
        await self._send_command("8103")

    async def bluetooth_pair(self):
        await self._send_command("8200")

    async def factory_reset(self):
        await self._send_command("8300")

    @staticmethod
    async def devices():
        devices = await BleakScanner.discover(service_uuids=[SERVICE_UUID])
        for device in devices:
            yield Z407Remote(device)