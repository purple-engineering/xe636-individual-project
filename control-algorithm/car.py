# Description: Program to run on the Microbit that receives the message sent from the Controller program. The message should be decoded, and the appropriate pins should be activated. Steering requests should be put through a PID algorithm.
# Author: Sonny Rickwood
# Version: 20230406-1352

# ========== Library Imports
from microbit import *
import radio

# ========== Microbit Config
radio.config(group=25, power=7, length=128, data_rate=radio.RATE_1MBIT)
display.off() # Required to use ADC pins

# ========== Pin Map
steering_pin = pin0 # Potentiometer Smaller = Right, Larger = Left
forw_p = pin6 # Drive Forward (Yellow)
back_p = pin9 # Drive Backward (Blue)
right_p = pin3 # Steering Right [Smaller Steering Value] (Green)
left_p = pin4 # Steering Left [Larger Steering Value] (White)

# ========== Steering Configuation
# Configurations to limit the steering due to physical steering column limits
steering_max = 850
steering_min = 200
steering_pos = (steering_max - steering_min)/2 + steering_min # Used for simulation and setting default steering position

# ========== Lambda Declaration
# Lambda declaration for converting a value from one range to another. Used for the gain values
mapping = lambda value, InitMin, InitMax, NewMin, NewMax : (((NewMax - NewMin)/(InitMax - InitMin)) * (value - InitMax)) + NewMax

# ========== Simulation Code
similation_status = False # Variable to determine whether or not to run simulation

# ========== Function Declaration
def steering_sim(left, right, lcl_steering_pos):
    # Local parameters determing simulation speed and adjustment speed of steering
    simulationSpeed = 200
    maxSteeringAdj = 100
    minSteeringAdj = -100
    
    # Code to check if dual input has been detected. 
    # If so code is halted and error message is displayed
    # Else next iteration of simulation is ran
    if bool(left) & bool(right):
        print("ERROR DUAL INPUT Left: {}, Right: {}".format(left, right))
        input()
    else:
        dir = left-right # Determine the requested steering value
        norm_dir = round(mapping(dir, -1023, 1023, minSteeringAdj, maxSteeringAdj), 2) 
        # Convert steering request to adjustment value
        # Then make sure min/max adjustment value is not exceeded
        if norm_dir > maxSteeringAdj:
            norm_dir = maxSteeringAdj
        elif norm_dir < minSteeringAdj:
            norm_dir = minSteeringAdj
        
        # Adjust the simulated steering value according to the adjustment
        lcl_steering_pos += norm_dir
        
        # Check to make sure the steering min/max is not exceeded
        if lcl_steering_pos > 1023:
            print("Steering Max Exceeded")
        elif lcl_steering_pos < 0:
            print("Steering Min Exceeded")
        
        # Precents the simulation from running too quickly
        sleep(simulationSpeed)
        return lcl_steering_pos

# ========== PID Code
# Initally set values to 0 if no value is obtained from controller
gbl_eP = 0
gbl_eI = 0
gbl_eD = 0
prev_timestamp = 0

def PID_algorithm(target, position, integral_error, delta_time, prev_error, Kp, Ki, Kd):
    # Determing the adjustment to be made to steering via a PID algorithm
    error = target - position # Proportional: Get the error value between the target/requested and the actual position
    integral_error += (error * delta_time) # Integral: Times the error by the time between iterations. Add the value to global variable.
    derivative_error = (error - prev_error)/ delta_time # Derivative: Calculate the rate the algorithm is adjusting

    output = (Kp * error) + (Ki * integral_error) + (Kd * derivative_error) # Sum the error values timesed by their gain values
    return output, error, integral_error, derivative_error

# ========== Function Declaration
def limit_func(target, min, max):
    # Function to limit a value to a range
    if target > max:
        return max
    elif target < min:
        return min
    else:
        return target

# ========== Main Code 
while True:
    # ========== Variable Reset
    # Clear the requested, gain and pin values.
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

    # ========== Radio Message Detection
    while True:
        # Keep looping until a Radio message is received
        controls = radio.receive()
        if controls:
            break
    controls = controls.strip('{').strip('}').split(',')

    # ========== Message Assignment
    for i, cont in enumerate(controls):
        # Assign requested values from Radio message to apppropriate local values
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
            # Converts requested steering to local steering limits to prevent requests above steering min/max

        if 'Gi' in cont:
            temp = cont.split(':')
            Gi = float(temp[1])

        if 'Gp' in cont:
            temp = cont.split(':')
            Gp = float(temp[1])

        if 'b' in cont:
            temp = cont.split(':')
            back_value = int(temp[1])

    
    # ========== PID Config
    curr_timestamp = running_time()
    deltaT = curr_timestamp - prev_timestamp
    prev_timestamp = curr_timestamp
    # Gets the delta time for the PID algorithm and sets variables for next iteration

    adjustment, gbl_eP, gbl_eI, gbl_eD = PID_algorithm(norm_requ_steer, steering_pos, gbl_eI, deltaT, gbl_eP, Gp, Gi, Gd)

    # ========== Steering Adjustments
    # Sets the left or right value according to the adjustment value returned from the PID algorithm
    # Unless the steering min/max is excessed which results in the opposing value to be assigned
    if adjustment > 0:
        if steering_pos > steering_max:
            right_value = adjustment
        else:
            left_value = adjustment  
    elif adjustment < 0:
        if steering_pos < steering_min:
            left_value = adjustment
        else:
            right_value = adjustment

    # Limits the value to ensure pins can be assigned the value
    left_value = limit_func(int(abs(left_value)), 0, 1023)
    right_value = limit_func(int(abs(right_value)), 0, 1023)
    
    # ========== Pin Assignment
    # Sets the pins accordingly
    forw_p.write_digital(forw_value)
    back_p.write_digital(back_value)
    left_p.write_analog(left_value)
    right_p.write_analog(right_value)

    # ========== Simulation
    if button_a.was_pressed():
        # Inverts simulation status if button A is pressed
        similation_status = not(similation_status)

    if similation_status == True:
        # Run simulation and correct steering_pos according to simulation
        steering_pos = steering_sim(left_value, right_value, steering_pos)
    else:
        # Else read the steering position
        steering_pos = steering_pin.read_analog()

    # ========== Code Debugging
    print("Req: {}, Pos: {}, Adj: {}, P: {}, I: {}, D: {}, Left: {}, Right: {}, Forward: {}, Backward: {}".format(norm_requ_steer, steering_pos, adjustment, gbl_eP * Gp, gbl_eI * Gi, gbl_eD * Gd, left_value, right_value, forw_value, back_value)) # Prints values for debugging purposes