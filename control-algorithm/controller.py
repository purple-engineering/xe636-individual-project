# Title: Remote Control Code
# Description:
# Author: Sonny Rickwood
# Version: 20230406-1352

# ========== Library Imports ====================
from microbit import *
import radio

# ========== Microbit Config ====================
radio.config(group=25, power=7, length=128, data_rate=radio.RATE_1MBIT)

mapping = lambda value, InitMin, InitMax, NewMin, NewMax : (((NewMax - NewMin)/(InitMax - InitMin)) * (value - InitMax)) + NewMax

# ========== Main Code ====================
while True:
    # ===== Dictionary Declaration ==========
    controls = {
        'f': 0, 
        'b': 0, 
        's':accelerometer.get_x(),
        'Gp': pin0.read_analog(),
        'Gi': pin1.read_analog(),
        'Gd': pin2.read_analog()
    }

    # ===== Gain Adjustments ==========
    controls['Gp'] = round(mapping(controls['Gp'], 0, 1023, 1, 10), 2)
    controls['Gi'] = 10 ** (-1 * round(mapping(controls['Gi'], 0, 1023, 6, 0), 2))
    controls['Gd'] = 10 ** (round(mapping(controls['Gd'], 0, 1023, 0, 5), 2))

    # ===== Steering Limits ==========
    if controls['s'] < -1023:
        controls['s'] = -1023
    elif controls['s'] > 1023:
        controls['s'] = 1023

    # ===== Direction Adjustment ==========
    if button_b.is_pressed():
        controls['f'] = 1
    elif button_a.is_pressed():
        controls['b'] = 1

    radio.send(str(controls))
    sleep(20)

    print("Forward: {}, Backward: {}, Steering: {}, Gp: {}, Gi: {}, Gd: {}".format(controls['f'], controls['b'], controls['s'], controls['Gp'], controls['Gi'], controls['Gd']))