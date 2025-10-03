const statusIndicator = document.getElementById("status-indicator");
const connectionMode = document.getElementById("connection-mode");
const bluetoothStatus = document.getElementById("bluetooth-status");

async function checkStatus() {
    try {
        const response = await fetch("/status");
        const data = await response.json();
        if (data.status === "connected") {
            statusIndicator.textContent = "Connected";
            statusIndicator.classList.remove("disconnected");
            statusIndicator.classList.add("connected");
            connectionMode.innerHTML = `<b>${data.connection_mode}</b>`;
            bluetoothStatus.innerHTML = `<b>${data.bluetooth_status}</b>`;
        } else {
            statusIndicator.textContent = "Disconnected";
            statusIndicator.classList.remove("connected");
            statusIndicator.classList.add("disconnected");
            connectionMode.textContent = "unknown";
            bluetoothStatus.innerHTML = "unknown";
        }
    } catch (error) {
        statusIndicator.textContent = "Error";
        statusIndicator.classList.remove("connected");
        statusIndicator.classList.add("disconnected");
        connectionMode.textContent = "unknown";
        bluetoothStatus.innerHTML = "unknown";
    }
}

async function callApi(endpoint) {
    try {
        const response = await fetch(endpoint, { method: "POST" });
        if (response.ok) {
            if (endpoint.startsWith("/input-")) {
                checkStatus();
            }
        } else {
            alert(`Error executing ${endpoint}: ${response.status}`);
        }
    } catch (error) {
        alert(`Failed to call ${endpoint}: ${error}`);
    }
}

setInterval(checkStatus, 3000);
checkStatus();
