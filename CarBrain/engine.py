import threading
import time
from GPIO import set_servo_pulsewidth, set_motor_pulsewidth, reset_servo_pulsewidth, reset_motor_pulsewidth, SERVO_CENTERED_PW, MOTOR_STOPPED_PW

AXIS_MAPPING = {
    0: "steering",
    6: "reverse",
    7: "throttle"
}

SERVO_NO_INPUT_STOP_DELAY = 0.2
MOTOR_NO_INPUT_STOP_DELAY = 0.2

servo_active = False
last_servo_input_time = None

motor_active = False
last_motor_input_time = None

def servo_input_monitor_loop():
    global last_servo_input_time
    global servo_active

    while servo_active:
        # Check if there has been any input in the last second
        if last_servo_input_time and time.time() - last_servo_input_time > SERVO_NO_INPUT_STOP_DELAY:
            servo_active = False
            reset_servo_pulsewidth()
        time.sleep(0.05)

def motor_input_monitor_loop():
    global last_motor_input_time
    global motor_active

    while motor_active:
        # Check if there has been any input in the last second
        if last_motor_input_time and time.time() - last_motor_input_time > MOTOR_NO_INPUT_STOP_DELAY:
            motor_active = False
            reset_motor_pulsewidth()
        time.sleep(0.05)


def handle_controller_input(axis_index: int, value: float):
    global last_servo_input_time, last_motor_input_time
    global servo_active, motor_active
    global latest_throttle_value, latest_reverse_value
    global last_forward_input_time, last_reverse_input_time

    # Validate input
    if value < -1 or value > 1:
        return

    # Map axis index to axis name
    axis_name = AXIS_MAPPING.get(axis_index)
    if axis_name is None:
        print(f"Unknown axis index: {axis_index}")
        return

    if axis_name == "steering":
        last_servo_input_time = time.time()
        if not servo_active:
            servo_active = True
            threading.Thread(target=servo_input_monitor_loop, daemon=True).start()

        set_servo_pulsewidth(int(SERVO_CENTERED_PW + (value * 300)))
        return

    if axis_name in ["throttle", "reverse"]:
        last_motor_input_time = time.time()
        if not motor_active:
            motor_active = True
            threading.Thread(target=motor_input_monitor_loop, daemon=True).start()

        if axis_name == "throttle":
            set_motor_pulsewidth(int(MOTOR_STOPPED_PW + (value * 300)))
        elif axis_name == "reverse":
            set_motor_pulsewidth(int(MOTOR_STOPPED_PW - (value * 300)))