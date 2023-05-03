# Description: A program capable of obtaining gain values, steering and forward/backward requests for the car. The requests will then be radioed to the other Microbit.
# Author: Sonny Rickwood
# Version: 20230406-1352

# ========== Library Imports
from microbit import *
import radio

# ========== Microbit Config
radio.config(group=25, power=7, length=128, data_rate=radio.RATE_1MBIT)
# Configuring Microbit radio to allow for message to be sent

# ========== Function Declaration
mapping = lambda value, InitMin, InitMax, NewMin, NewMax : (((NewMax - NewMin)/(InitMax - InitMin)) * (value - InitMax)) + NewMax
# Lambda declaration for converting a value from one range to another. Used for the gain values

# ========== Main Code
while True:
    # ========== Dictionary Declaration
    # Dictionary containing requested values from the controller
    controls = {
        'f': 0, 
        'b': 0, 
        's':accelerometer.get_x(),
        'Gp': pin0.read_analog(),
        'Gi': pin1.read_analog(),
        'Gd': pin2.read_analog()
    }

    # ========== Gain Adjustments
    # Adjusting the Gain values to better suit their effect on the PID algorithm
    controls['Gp'] = round(mapping(controls['Gp'], 0, 1023, 1, 10), 2)
    controls['Gi'] = 10 ** (-1 * round(mapping(controls['Gi'], 0, 1023, 6, 0), 2))
    controls['Gd'] = 10 ** (round(mapping(controls['Gd'], 0, 1023, 0, 5), 2))

    # ========== Steering Limits
    # Limits the steering to +/- 1023 to prevent PID algorithm exceeding values
    if controls['s'] < -1023:
        controls['s'] = -1023
    elif controls['s'] > 1023:
        controls['s'] = 1023

    # ========== Direction Adjustment
    # Adjusts forward/backward requests according to buttons pressed
    if button_b.is_pressed():
        controls['f'] = 1
    elif button_a.is_pressed():
        controls['b'] = 1

    radio.send(str(controls))
    sleep(20)
    # Sends the requested values and delays from program to restrict message requests

    print("Forward: {}, Backward: {}, Steering: {}, Gp: {}, Gi: {}, Gd: {}".format(controls['f'], controls['b'], controls['s'], controls['Gp'], controls['Gi'], controls['Gd']))
    # Prints for debugging