import startGamepad from "./gamepad.js";
import startWebRTCConnection from "./webrtc.js";

const { localConnection, dataChannel, sendData } = startWebRTCConnection();

const gamepadPollInterval = 25;

// Send gamepad data to car
function gamepadInputCallback(axisIndex, value) {
    // Ignore axes and buttons that are not used
    if (![0, 6, 7].includes(axisIndex)) return;

    // Rounding to reduce data size
    const roundedValue = Math.round(value * 100) / 100;

    // If open data channel, send data to car in format: "axisIndex,roundedValue"
    if (localConnection.connectionState === "connected") {
        sendData(`${axisIndex},${roundedValue}`);
    }
}
startGamepad(gamepadPollInterval, gamepadInputCallback);

// Ping/pong to calculate latency
let latestPing = null;
setInterval(() => {
    if (localConnection.connectionState !== "connected") return;

    // Return if a ping is already in flight
    if (latestPing) {
        return;
    }

    latestPing = Date.now();
    sendData(latestPing);
}, 500);

dataChannel.onmessage = (event) => {
    const pong = parseInt(event.data);

    // Calculate latency
    const latency = pong - latestPing;
    document.getElementById("dataLatency").textContent = `${latency}ms`;
    latestPing = null;
};
