/*  Updates the gamepad UI based on input and calls callback functions
    for axis and button input. The callback functions are passed as arguments
    to the startGamepad function. */

// Firefox detection and warning
const isFirefox = typeof InstallTrigger !== "undefined";
if (typeof InstallTrigger !== "undefined") {
    console.error = "Firefox gamepad API does not support pressure sensitive triggers - this is needed for controlling cars speed. Please use a chromium-based browser instead.";
    alert("Use a chromium-based browser, read console for more info.");
}

// Change status indicator color when gamepad is connected/disconnected
window.addEventListener("gamepadconnected", function (e) {
    document.querySelector(".statusIndicator").style.backgroundColor = "green";
    document.getElementById("gamepadStatus").textContent = "Connected";
});
window.addEventListener("gamepaddisconnected", function (e) {
    document.querySelector(".statusIndicator").style.backgroundColor = "red";
    document.getElementById("gamepadStatus").textContent = "Disconnected";
});

const buttonMapping = {
    // Buttons
    3: "buttons_up",
    1: "buttons_right",
    2: "buttons_left",
    0: "buttons_down",
    // Arrows
    12: "arrows_up",
    15: "arrows_right",
    13: "arrows_down",
    14: "arrows_left",
    // Left triggers
    4: "leftTriggers_up",
    6: "leftTriggers_down",
    // Right triggers
    5: "rightTriggers_up",
    7: "rightTriggers_down",
};

// Reset the gamepad input elements
function resetControllerUI() {
    // Buttons
    Object.values(buttonMapping).forEach((buttonClass, index) => {
        let element = document.querySelector(`.${buttonClass}`);
        element.style.background = "rgb(0, 0, 0, 0.1)";
    });

    // Stick positioning
    document.querySelector(".leftStick_dot").style.left = "50%";
    document.querySelector(".leftStick_dot").style.top = "50%";
    document.querySelector(".rightStick_dot").style.left = "50%";
    document.querySelector(".rightStick_dot").style.top = "50%";

    // Stick opacity
    document.querySelector(".leftStick_dot").style.background = "rgb(0, 0, 0, 0.1)";
    document.querySelector(".rightStick_dot").style.background = "rgb(0, 0, 0, 0.1)";
}

function updateButtonUI(buttonIndex, value) {
    const action = buttonMapping[buttonIndex];

    if (action) {
        const element = document.querySelector(`.${action}`);

        // Bottom left/right triggers which are pressure sensitive
        if (buttonIndex === 6 || buttonIndex === 7) {
            // Calculate gradient percentage
            let percentage = value * 100;

            // Apply a linear gradient from either left or right, and overlay it with black at 0.1 opacity
            const to = buttonIndex === 6 ? "left" : "right";
            element.style.background = `linear-gradient(to ${to}, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1)), linear-gradient(to ${to}, black ${percentage}%, transparent ${percentage}%)`;
        } else {
            element.style.backgroundColor = "rgba(0, 0, 0, 1)";
        }
    }
}

function updateAxisUI(axisIndex, value) {
    const leftStickDot = document.querySelector(".leftStick_dot");
    const rightStickDot = document.querySelector(".rightStick_dot");

    // Map the axis value from [-1, 1] to [0%, 100%]
    const position = ((value + 1) / 2) * 100;

    // Update position for left or right stick dot and calculate opacity
    function handleStickDot(stick, axisIndex1, axisIndex2) {
        stick.style.left = axisIndex === axisIndex1 ? `${position}%` : stick.style.left;
        stick.style.top = axisIndex === axisIndex2 ? `${position}%` : stick.style.top;

        const horizontalDistance = Math.abs((stick.style.left.replace("%", "") || 50) - 50);
        const verticalDistance = Math.abs((stick.style.top.replace("%", "") || 50) - 50);
        const maxDistance = Math.max(horizontalDistance, verticalDistance);
        const opacity = Math.max(maxDistance / 50, 0.1);

        stick.style.backgroundColor = `rgba(0, 0, 0, ${opacity})`;
    }

    // Left or right stick
    if (axisIndex === 0 || axisIndex === 1) {
        handleStickDot(leftStickDot, 0, 1);
    } else if (axisIndex === 2 || axisIndex === 3) {
        handleStickDot(rightStickDot, 2, 3);
    }
}

export default function startGamepad(pollInterval, gamepadInputCallback) {
    setInterval(() => {
        let hasInput = false;

        const gamepad = navigator.getGamepads()[0];
        resetControllerUI();

        if (gamepad) {
            // Buttons
            gamepad.buttons.forEach((button, index) => {
                if (button.value > 0) {
                    updateButtonUI(index, button.value);

                    hasInput = true;
                }
            });

            // Axes
            gamepad.axes.forEach((axis, index) => {
                // Circumvent minimal stick drift
                if (axis > 0.075 || axis < -0.075) {
                    updateAxisUI(index, axis);

                    hasInput = true;
                }
            });

            // Callback if any input
            if (hasInput && gamepadInputCallback) {
                gamepadInputCallback(gamepad);
            }
        }
    }, pollInterval);
}
