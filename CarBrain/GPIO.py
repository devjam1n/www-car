import RPi.GPIO as GPIO

# Both of these are in BOARD numbering scheme
SERVO_PIN = 32
MOTOR_PIN = 33
# Default PWM values for servo and motor
SERVO_CENTERED_PWN = 6.7
MOTOR_STOPPED_PWN = 7.1

# Setup
GPIO.setmode(GPIO.BOARD)  # Use BOARD numbering scheme
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# PWN frequency
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
motor_pwm = GPIO.PWM(MOTOR_PIN, 50)

def start_PWN():
    servo_pwm.start(SERVO_CENTERED_PWN)
    motor_pwm.start(MOTOR_STOPPED_PWN)

def set_servo_position(position):
    servo_pwm.ChangeDutyCycle(position)
    print(f"Servo position set to {position}")

def set_motor_position(position):
    motor_pwm.ChangeDutyCycle(position)
    print(f"Motor position set to {position}")

def cleanup():
    servo_pwm.stop()
    motor_pwm.stop()
    GPIO.cleanup()
    print("GPIO cleanup complete")