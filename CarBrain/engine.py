import threading
import time
from GPIO import set_servo_pulsewidth, set_motor_pulsewidth, reset_servo_pulsewidth, reset_motor_pulsewidth, SERVO_CENTERED_PW, MOTOR_STOPPED_PW

AXIS_MAPPING = {
    0: "sterring",
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


def handle_controller_input(throttle: float, steering: float):
    global last_servo_input_time, last_motor_input_time
    global servo_active, motor_active
    global latest_throttle_value, latest_reverse_value
    global last_forward_input_time, last_reverse_input_time

    # Validate throttle and steering inputs
    if not -1 <= throttle <= 1 or not -1 <= steering <= 1:
        print("Invalid throttle or steering value. Values must be between -1 and 1.")
        return

    # Handle steering input
    last_servo_input_time = time.time()
    if not servo_active and steering != 0:
        servo_active = True
        threading.Thread(target=servo_input_monitor_loop, daemon=True).start()

    # Adjust servo position based on steering value
    set_servo_pulsewidth(int(SERVO_CENTERED_PW + (steering * 300)))

    # Handle throttle input
    last_motor_input_time = time.time()
    if not motor_active and throttle != 0:
        motor_active = True
        threading.Thread(target=motor_input_monitor_loop, daemon=True).start()

    if throttle >= 0:
        # Forward throttle
        set_motor_pulsewidth(int(MOTOR_STOPPED_PW + (throttle * 300)))
    else:
        # Reverse throttle
        set_motor_pulsewidth(int(MOTOR_STOPPED_PW + (throttle * 300)))  # Assuming reverse is handled similarly

