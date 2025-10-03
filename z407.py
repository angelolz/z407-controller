import asyncio
import logging
from enum import Enum
from typing import Optional

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic

# Constants
SERVICE_UUID = "0000fdc2-0000-1000-8000-00805f9b34fb"
COMMAND_UUID = "c2e758b9-0e78-41e0-b0cb-98a593193fc5"
RESPONSE_UUID = "b84ac9c6-29c5-46d4-bba1-9d534784330f"

logger = logging.getLogger("z407")
logger.setLevel(logging.INFO)

class ConnectionMode(Enum):
    DISCONNECTED = "disconnected"
    BLUETOOTH = "bluetooth"
    AUX = "aux"
    USB = "usb"


class BluetoothStatus(Enum):
    UNKNOWN = "unknown"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PAIRING = "pairing"


class Z407Remote:
    def __init__(self, address: str):
        self.address = address
        self.client = BleakClient(address)
        self.connection_mode: ConnectionMode = ConnectionMode.DISCONNECTED
        self.bluetooth_status: BluetoothStatus = BluetoothStatus.UNKNOWN
        self.connected: bool = False

    async def connect(self, timeout: float = 10.0) -> bool:
        """Connect and set up notifications."""
        try:
            logger.info("Connecting to %s...", self.address)
            await asyncio.wait_for(self.client.connect(), timeout=timeout)

            await self.client.start_notify(RESPONSE_UUID, self._receive_data)
            await self._send_command("8405")  # initial handshake?
            logger.info("Connected and notifications enabled.")
            return True
        except Exception as e:
            logger.error("Failed to connect: %s", e)
            return False

    async def disconnect(self):
        """Gracefully disconnect."""
        if self.client.is_connected:
            logger.info("Disconnecting...")
            await self.client.disconnect()
        self.connected = False
        self.connection_mode = ConnectionMode.DISCONNECTED

    async def __aenter__(self):
        await self.connect()
        return self  # return self so "async with Z407Remote(...)" works

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def _receive_data(self, sender: BleakGATTCharacteristic, data: bytearray):
        """Handle incoming notifications from the speaker."""
        handlers = {
            b"\xd4\x05\x01": self._on_initial_connection,
            b"\xcf\x0b": lambda: logger.info("Connecting..."),
            b"\xd4\x00\x01": lambda: self._set_connected(ConnectionMode.BLUETOOTH),
            b"\xd4\x00\x02": lambda: self._set_connected(ConnectionMode.AUX),
            b"\xd4\x00\x03": lambda: self._set_connected(ConnectionMode.USB),
            b"\xc0\x02": lambda: logger.info("Received volume up"),
            b"\xc0\x03": lambda: logger.info("Received volume down"),
            b"\xc0\x04": lambda: logger.info("Received play/pause"),
            b"\xc1\x01": lambda: self._switch_input(ConnectionMode.BLUETOOTH),
            b"\xc1\x02": lambda: self._switch_input(ConnectionMode.AUX),
            b"\xc1\x03": lambda: self._switch_input(ConnectionMode.USB),
            b"\xcf\x00": lambda: self._set_bt_status(BluetoothStatus.CONNECTED),
            b"\xcf\x01": lambda: self._set_bt_status(BluetoothStatus.DISCONNECTED),
            b"\xc2\x00": lambda: self._set_bt_status(BluetoothStatus.PAIRING),
            b"\xcf\x04": lambda: self._set_connected(ConnectionMode.BLUETOOTH),
            b"\xcf\x05": lambda: self._set_connected(ConnectionMode.AUX),
            b"\xcf\x06": lambda: self._set_connected(ConnectionMode.USB),
            b"\xc3\x00": self._on_factory_reset,
        }

        handler = handlers.get(bytes(data))
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
        else:
            logger.warning("Unknown command: %s", data.hex(" "))

    async def _send_command(self, command: str):
        """Send hex string command to the speaker."""
        try:
            await self.client.write_gatt_char(COMMAND_UUID, bytes.fromhex(command), response=False)
            logger.debug("Sent command: %s", command)
        except Exception as e:
            logger.error("Failed to send command %s: %s", command, e)

    async def _on_initial_connection(self):
        logger.info("Initial connection...")
        await self._send_command("8400")

    def _set_connected(self, mode: ConnectionMode):
        self.connected = True
        self.connection_mode = mode
        logger.info("Connected! Mode: %s", mode.value)

    def _switch_input(self, mode: ConnectionMode):
        if self.connection_mode == mode:
            logger.info("Speakers already set to %s.", mode.value)
        else:
            logger.info("Switching to %s...", mode.value)

    def _set_bt_status(self, status: BluetoothStatus):
        self.bluetooth_status = status
        logger.info("Bluetooth status: %s", status.value)

    def _on_factory_reset(self):
        self.bluetooth_status = BluetoothStatus.DISCONNECTED
        logger.warning("Device has been reset.")

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
        """Yield discovered Z407 devices with matching service UUID."""
        devices = await BleakScanner.discover(service_uuids=[SERVICE_UUID])
        for device in devices:
            yield Z407Remote(device.address)
