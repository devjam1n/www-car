import threading
import time
from GPIO import start_servo, start_motor, set_servo_position, set_motor_position

# Default PWM values for servo and motor
SERVO_CENTERED_PWN = 6.7
MOTOR_STOPPED_PWN = 7.1
AXIS_MAPPING = {
    0: "steering",
    6: "reverse",
    7: "throttle"
}

# To keep track of whether the motor/servo is active or not
motor_active = False
servo_active = False
# To stop the motor/servo if there has been no input in 0.2 seconds
last_motor_input_time = None
last_servo_input_time = None
# To perform smooth forward/backward transitions
last_throttle_input = 0
last_reverse_input = 0
# To avoid unnecessary motor position updates
last_motor_pwn = MOTOR_STOPPED_PWN


def start_servo():
    global servo_active
    servo_active = True
    start_servo(SERVO_CENTERED_PWN)
    print("Servo now active")

    # Input monitoring loop as a background thread
    input_monitor_thread = threading.Thread(target=servo_input_monitor_loop)
    input_monitor_thread.daemon = True
    input_monitor_thread.start()


def start_motor():
    global motor_active
    motor_active = True
    start_motor(SERVO_CENTERED_PWN, MOTOR_STOPPED_PWN)
    print("Motor now active")

    # Input monitoring loop as a background thread
    input_monitor_thread = threading.Thread(target=motor_input_monitor_loop)
    input_monitor_thread.daemon = True
    input_monitor_thread.start()


def stop_motor():
    global motor_active
    motor_active = False
    set_motor_position(MOTOR_STOPPED_PWN)
    print(f"Motor position reset to default: {MOTOR_STOPPED_PWN}")


def stop_servo():
    global servo_active
    servo_active = False
    set_servo_position(SERVO_CENTERED_PWN)
    print(f"Servo position reset to default: {SERVO_CENTERED_PWN}")


def motor_input_monitor_loop():
    global last_motor_input_time
    global motor_active

    while motor_active:
        # Check if there has been any input in the last second
        if last_motor_input_time and time.time() - last_motor_input_time > 0.2:
            stop_motor()
        time.sleep(0.1)


def servo_input_monitor_loop():
    global last_servo_input_time
    global servo_active

    while servo_active:
        # Check if there has been any input in the last second
        if last_servo_input_time and time.time() - last_servo_input_time > 0.2:
            stop_servo()
        time.sleep(0.1)


def handle_controller_input(axis_index: int, value: float):
    global last_motor_input_time
    global last_servo_input_time
    global motor_active
    global last_reverse_input
    global last_throttle_input

    # Validate input
    if value < -1 or value > 1:
        return

    # Map axis index to axis name
    axis_name = AXIS_MAPPING.get(axis_index)
    if axis_name is None:
        print(f"Unknown axis index: {axis_index}")
        return

    # Handle axis input
    if axis_name == "steering":
        last_servo_input_time = time.time()

        # Stopped servo? Let's start it
        if not servo_active:
            start_servo()
            return

        # DEL, set_servo_position(SERVO_CENTERED_PWN + value)
        intency = value / 5

        servo_position = SERVO_CENTERED_PWN * (intency + 1)
        servo_position_rounded = round(servo_position, 1)

        print(f"Servo position set to {servo_position_rounded}")
        set_servo_position(servo_position_rounded)
    elif axis_name == "reverse":
        last_reverse_input = value
        update_motor_position()
    elif axis_name == "throttle":
        last_throttle_input = value
        update_motor_position()


def update_motor_position():
    global last_motor_input_time
    global motor_active

    global last_reverse_input
    global last_throttle_input
    global last_motor_pwn

    try:
        last_motor_input_time = time.time()

        # Stopped motor? Let's start it
        if not motor_active:
            start_motor()
            return

        THROTTLE_THRESHOLD = 0.1

        # Calculate intensity for throttle and brake
        throttle_intensity = max(
            0, (last_throttle_input - THROTTLE_THRESHOLD) / 5)
        brake_intensity = last_reverse_input / 5

        # Determine the effective motor position based on throttle and brake inputs
        if last_throttle_input >= last_reverse_input:
            # If throttle is greater or equal, move forward or stay still
            motor_position = round(
                MOTOR_STOPPED_PWN * (1 + throttle_intensity - brake_intensity), 1)
        else:
            # If brake is greater, potentially move backward
            motor_position = round(MOTOR_STOPPED_PWN *
                                   (1 - brake_intensity), 1)

        # Safety to not exceed certain thresholds
        # motor_position = max(min_motor_position, min(motor_position, max_motor_position))

        if motor_position == last_motor_pwn:
            return
        last_motor_pwn = motor_position

        print(f"Motor position set to {motor_position}")
        set_motor_position(motor_position)
    except Exception as e:
        print(f"Error updating motor position: {e}")
