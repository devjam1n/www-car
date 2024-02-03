import startGamepad from "./gamepad.js";
import startWebRTCConnection from "./webrtc.js";

const { localConnection, dataChannel, sendData } = startWebRTCConnection();

const gamepadPollInterval = 25;
const forwardMarginIfAlsoReverse = 0.25;

// Helper to round to max. two decimal places
function roundToTwo(num) {
    return Math.round(num * 100) / 100;
}

// Run every time a gamepad input is detected
function gamepadInputCallback(gamepad) {
    // Forward and reverse format: 0-1
    const forwardValue = gamepad.buttons[7].value; // Right trigger
    const reverseValue = gamepad.buttons[6].value; // Left trigger
    // Sterring format: -1 to 1
    let sterringValue = gamepad.axes[0]; // Left stick horizontal axis

    // Circumvent minimal stick drift
    if (sterringValue > -0.075 && sterringValue < 0.075) {
        sterringValue = 0;
    }

    // Calculate throttle control (smooth forward and reverse simontaneously)
    const forwardLessIfBackwards = reverseValue > 0 ? forwardValue - forwardMarginIfAlsoReverse : forwardValue;
    const throttleValue = roundToTwo(forwardLessIfBackwards - reverseValue);
    const throttleValueMinMax = Math.min(1, Math.max(-1, throttleValue));

    // Format: throttle,sterring
    const dataString = `${throttleValueMinMax},${roundToTwo(sterringValue)}`;

    // Send data if connected
    if (localConnection.connectionState === "connected") {
        console.log(dataString);
        sendData(dataString);
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
}, 5000);

dataChannel.onmessage = (event) => {
    const pong = parseInt(event.data);

    // Calculate latency
    const latency = pong - latestPing;
    document.getElementById("dataLatency").textContent = `${latency}ms`;
    latestPing = null;
};
