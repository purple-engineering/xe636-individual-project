# Title: Remote Control Car Code with Simulation
# Description:
# Author: Sonny Rickwood
# Version: 20230406-1352

# ========== Library Imports ====================
from microbit import *
import radio

# ========== Microbit Config ====================
radio.config(group=25, power=7, length=128, data_rate=radio.RATE_1MBIT)
display.off()

# ========== Pin Map ====================
steering_pin = pin0 # Potentiometer Smaller = Right, Larger = Left
forw_p = pin6 # Drive Forward (Yellow)
back_p = pin9 # Drive Backward (Blue)
right_p = pin3 # Steer Smaller (Green/Right)
left_p = pin4 # Steer Larger (White/Left)

# ========== Steering Configuation ====================
steering_max = 850
steering_min = 200
steering_pos = (steering_max - steering_min)/2 + steering_min

# ========== Lambda Declaration ====================
mapping = lambda value, InitMin, InitMax, NewMin, NewMax : (((NewMax - NewMin)/(InitMax - InitMin)) * (value - InitMax)) + NewMax

# ========== Simulation Code ====================
similation_status = False

def steering_sim(left, right, lcl_steering_pos):
    simulationSpeed = 200
    maxSteeringAdj = 100
    minSteeringAdj = -100
    
    if bool(left) & bool(right):
        print("ERROR DUAL INPUT Left: {}, Right: {}".format(left, right))
        input()
    else:
        dir = left-right
        norm_dir = round(mapping(dir, -1023, 1023, minSteeringAdj, maxSteeringAdj), 2)
        if norm_dir > maxSteeringAdj:
            norm_dir = maxSteeringAdj
        elif norm_dir < minSteeringAdj:
            norm_dir = minSteeringAdj
            
        lcl_steering_pos += norm_dir

        if lcl_steering_pos > 1023:
            print("Steering Max Exceeded")
        elif lcl_steering_pos < 0:
            print("Steering Min Exceeded")
        
        sleep(simulationSpeed)
        return lcl_steering_pos


# ========== PID Code ====================
gbl_eP = 0
gbl_eI = 0
gbl_eD = 0
prev_timestamp = 0

def PID_algorithm(target, position, integral_error, delta_time, prev_error, Kp, Ki, Kd):
    error = target - position
    integral_error += (error * delta_time)
    derivative_error = (error - prev_error)/ delta_time

    output = (Kp * error) + (Ki * integral_error) + (Kd * derivative_error)
    return output, error, integral_error, derivative_error

# ========== Function Declaration ====================
def limit_func(target, min, max):
    if target > max:
        return max
    elif target < min:
        return min
    else:
        return target

# ========== Main Code ====================
while True:
    # ===== Variable Reset ==========
    controls = ""
    requ_steer = 0
    norm_requ_steer = 0
    
    Gp = 0
    Gi = 0
    Gd = 0

    forw_value = 0
    back_value = 0
    left_value = 0
    right_value = 0

    # ===== Radio Message Detection ==========
    while True:
        controls = radio.receive()
        if controls:
            break
    controls = controls.strip('{').strip('}').split(',')

    # ===== Message Assignment ==========
    for i, cont in enumerate(controls):
        if 'Gd' in cont:
            temp = cont.split(':')
            Gd = float(temp[1])
            
        if 'f' in cont:
            temp = cont.split(':')
            forw_value = int(temp[1])

        if 's' in cont:
            temp = cont.split(':')
            requ_steer = mapping(int(temp[1]), -1023, 1023, steering_min, steering_max)
            norm_requ_steer = limit_func(requ_steer, steering_min, steering_max)

        if 'Gi' in cont:
            temp = cont.split(':')
            Gi = float(temp[1])

        if 'Gp' in cont:
            temp = cont.split(':')
            Gp = float(temp[1])

        if 'b' in cont:
            temp = cont.split(':')
            back_value = int(temp[1])

    
    # ===== PID Config ==========
    curr_timestamp = running_time()
    deltaT = curr_timestamp - prev_timestamp
    prev_timestamp = curr_timestamp

    adjustment, gbl_eP, gbl_eI, gbl_eD = PID_algorithm(norm_requ_steer, steering_pos, gbl_eI, deltaT, gbl_eP, Gp, Gi, Gd)

    # ===== Steering Adjustments ==========
    if adjustment > 0:
        if steering_pos > steering_max:
            right_value = adjustment
            inverted = True
        else:
            left_value = adjustment  
    elif adjustment < 0:
        if steering_pos < steering_min:
            left_value = adjustment
            inverted = True
        else:
            right_value = adjustment

    left_value = limit_func(int(abs(left_value)), 0, 1023)
    right_value = limit_func(int(abs(right_value)), 0, 1023)
    
    # ===== Pin Assignment ==========
    forw_p.write_digital(forw_value)
    back_p.write_digital(back_value)
    left_p.write_analog(left_value)
    right_p.write_analog(right_value)

    # ===== Simulation ==========
    if button_a.was_pressed():
        similation_status = not(similation_status)

    if similation_status == True:
        steering_pos = steering_sim(left_value, right_value, steering_pos)
    else:
        steering_pos = steering_pin.read_analog()

    # ===== Code Testing ==========
    print("Req: {}, Pos: {}, Adj: {}, P: {}, I: {}, D: {}, Left: {}, Right: {}, Forward: {}, Backward: {}".format(norm_requ_steer, steering_pos, adjustment, gbl_eP * Gp, gbl_eI * Gi, gbl_eD * Gd, left_value, right_value, forw_value, back_value))