import RPi.GPIO as GPIO

# Both of these are in BOARD numbering scheme
SERVO_PIN = 32
MOTOR_PIN = 33

# Setup
GPIO.setmode(GPIO.BOARD)  # Use BOARD numbering scheme
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# PWN frequency
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
motor_pwm = GPIO.PWM(MOTOR_PIN, 50)

def start_PWN(servo_position, motor_position):
    servo_pwm.start(servo_position)
    motor_pwm.start(motor_position)

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