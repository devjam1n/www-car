import threading
import time
from GPIO import set_servo_pulsewidth, set_motor_pulsewidth, reset_servo_pulsewidth, reset_motor_pulsewidth, SERVO_CENTERED_PW, MOTOR_STOPPED_PW

# Constants
SERVO_NO_INPUT_STOP_DELAY = 0.2
MOTOR_NO_INPUT_STOP_DELAY = 0.2
STERRING_RANGE = 400
THROTTLE_RANGE = 300

# Variables
servo_active = False
motor_active = False
last_sterring_input_time = None
last_throttle_input_time = None
last_servo_pw = SERVO_CENTERED_PW
last_motor_pw = MOTOR_STOPPED_PW


# Monitor last input time for servo and motor and stop if no input is received after a certain delay
def servo_input_monitor_loop():
    global last_sterring_input_time
    global servo_active

    while servo_active:
        if last_sterring_input_time and time.time() - last_sterring_input_time > SERVO_NO_INPUT_STOP_DELAY:
            servo_active = False
            reset_servo_pulsewidth()
        time.sleep(0.05)
def motor_input_monitor_loop():
    global last_throttle_input_time
    global motor_active

    while motor_active:
        if last_throttle_input_time and time.time() - last_throttle_input_time > MOTOR_NO_INPUT_STOP_DELAY:
            motor_active = False
            reset_motor_pulsewidth()
        time.sleep(0.05)

# From controller input set servo and motor pulse width and start/stop input monitor threads
def handle_controller_input(throttle: float, steering: float):
    global last_sterring_input_time, last_throttle_input_time
    global servo_active, motor_active
    global latest_throttle_value, latest_reverse_value
    global last_forward_input_time, last_reverse_input_time
    global last_servo_pw, last_motor_pw

    # Validate throttle and steering inputs
    if not -1 <= throttle <= 1 or not -1 <= steering <= 1:
        print("Invalid throttle or steering value. Values must be between -1 and 1.")
        return

    if steering != 0:
        last_sterring_input_time = time.time()
        if not servo_active:
            servo_active = True
            threading.Thread(target=servo_input_monitor_loop, daemon=True).start()

    # Convert steering input to pulse width
    servo_pw = int(SERVO_CENTERED_PW + (steering * STERRING_RANGE))
    # Set steering pulse width if it has changed
    if servo_pw != last_servo_pw:
        set_servo_pulsewidth(servo_pw)
        last_servo_pw = servo_pw

    if throttle != 0:
        last_throttle_input_time = time.time()
        if not motor_active:
            motor_active = True
            threading.Thread(target=motor_input_monitor_loop, daemon=True).start()

        # Convert throttle input to pulse width
        motor_pw = int(MOTOR_STOPPED_PW + (throttle * THROTTLE_RANGE))
        # Set motor pulse width if it has changed
        if motor_pw != last_motor_pw:
            set_motor_pulsewidth(motor_pw)
            last_motor_pw = motor_pw

