# Configure GPIO pins and pulse width constants here

import pigpio # pigpio instead of RPi.GPIO for hardware PWM (must run as service)

# BCM numbering scheme
SERVO_PIN = 12
MOTOR_PIN = 13
# Default pulse width for servo and motor
SERVO_CENTERED_PW = 1500
MOTOR_STOPPED_PW = 1500

# Initialize pigpio library and GPIO pin
pi = pigpio.pi()
if not pi.connected:
    exit()

# Functions to set servo/motor pulse width
def set_servo_pulsewidth(pulse_width):
    # Validate pulse width
    if pulse_width < 500 or pulse_width > 2500:
        print("Invalid pulse width")

    # Set pulse width
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
    print(f"Servo pulse width set to {pulse_width}")

def set_motor_pulsewidth(pulse_width):
    if pulse_width < 500 or pulse_width > 2500:
        print("Invalid pulse width")

    pi.set_servo_pulsewidth(MOTOR_PIN, pulse_width)
    print(f"Motor pulse width set to {pulse_width}")

# Functions to reset pulse width of servo/motor (centered/stopped)
def reset_servo_pulsewidth():
    set_servo_pulsewidth(SERVO_CENTERED_PW)
    print(f"Servo position reset to default: {SERVO_CENTERED_PW}")

def reset_motor_pulsewidth():
    set_motor_pulsewidth(MOTOR_STOPPED_PW)
    print(f"Motor position reset to default: {MOTOR_STOPPED_PW}")

#pi.stop()