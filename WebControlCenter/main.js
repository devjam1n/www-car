import startGamepad from "./gamepad.js";
import startWebRTCConnection from "./webrtc.js";

const { localConnection, sendData } = startWebRTCConnection();

const gamepadPollInterval = 25;

function gamepadInputCallback(axisIndex, value) {
    // Ignore axes and buttons that are not used
    if (![0, 6, 7].includes(axisIndex)) return;

    // Rounding to reduce data size
    const roundedValue = Math.round(value * 100) / 100;

    // Send data to car in format: axisIndex,value
    sendData(`${axisIndex},${roundedValue}`);
}

startGamepad(gamepadPollInterval, gamepadInputCallback);
