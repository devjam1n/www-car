import startGamepad from "./gamepad.js";
import startWebRTCConnection from "./webrtc.js";

startWebRTCConnection();

const gamepadPollInterval = 25;

function handleAxisMove(axisIndex, value) {
    console.log(`Axis ${axisIndex} moved to ${value}`);
}

function handleButtonPress(buttonIndex, value) {
    console.log(`Button ${buttonIndex} pressed with value ${value}`);
}

startGamepad(gamepadPollInterval, handleAxisMove, handleButtonPress);
