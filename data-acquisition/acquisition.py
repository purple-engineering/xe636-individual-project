# Description: A program that acquires and stores the acceleration data onboard the Microbit.
# Author: Sonny Rickwood
# Version: 20230428-1325


# ========== Library Imports
from microbit import *
import radio, log, speech

# ========== Microbit Configuration
accelerometer.set_range(8) # Range: 0-8, Default: 8
global_radio_group = 255 # Range: 0-255, Default: 255
radio.config(group=global_radio_group, power=7)
radio.on()

# ========== Start/Safety Procedure
message = radio.receive()

while message != "Confirm Launch":
    # Loop to check if a message has been received from the other Microbit
    # If the message does not match "Confirm Launch", code will keep looping
    # Or until Button A is pressed on the Microbit
    # This will result in the Microbit sending out Launch Confirmation message
    message = radio.receive()
    if button_a.was_pressed():
        radio.send("Confirm Launch")
        break
    display.show(Image.NO)

# ========== Start Confirmation
# Code to confirm to the user that the accelerometer calibration procedure is about to start
display.show(Image.NO.invert()) # Inverts the "No" image previously shown
radio.off() # Radio turned off to save power
log.delete(True) # Clears Microbit memory ready for data acquisition
set_volume(255)

# ========== Accelerometer Calibration
cali_dict = {'x':0, 'y':0, 'z':0, 'len':0} # Creates a dictionary to store the biasing values and length of biasing data
wait_len, slp_len, last_time = 10000, 100, 0
# wait_len: Duration of the loop (ms)
# slp_len: Pauses between each iteration (ms)
# last_time: Used for displaying the amount of time left before calibration process is complete.

while wait_len > 0:
    # Loop that keeps iterating until wait_len is less then 0
    # Loops iteration length is equal to wait_len/slp_Len
    # Each iteration results in acceleration data being added to their respective dictionary and len increasing by 1
       
    accel_x, accel_y, accel_z = accelerometer.get_values()
    
    cali_dict['x'] += accel_x
    cali_dict['y'] += accel_y
    cali_dict['z'] += accel_z
    
    cali_dict['len'] += 1
    wait_len -= slp_len

    time = wait_len // 1000 # Floor divided the remaining time by 1000 to give the number of whole seconds left in the loop
    
    if last_time != time:
        # Checks to see if the last number shown/said is different from the current.
        # If it is different the new number is shown/said
        # Else it continues
        speech.say(str(time))
        last_time = time
        display.show(Image.ALL_CLOCKS[time])
    sleep(slp_len)

# Dictionary to contain biasing data 
avg_dict = {'x':cali_dict['x']/cali_dict['len'], 
            'y':cali_dict['y']/cali_dict['len'], 
            'z':cali_dict['z']/cali_dict['len']}

# ========== Start Logging Confirmation
# Code to confirm to user that data logging is about to start
for x in range(0, 3):
    display.show(Image.SQUARE)
    sleep(100)
    display.show(Image.SQUARE.invert())
    sleep(100)
    speech.say('Go')

# ========== Data Acquisition & Logging
# Data is logged to Microbits onboard memory with the current running time
# Logging can be halted if button B is pressed
# Confirmation of logging is displayed through Microbit screen
display.show(Image.HAPPY)
while not(button_b.was_pressed()):
    # Logs biased acceleration data every 200 ms until button B is pressed
    # Delay is added to prevent memory overflow
    data = {'x': str(accelerometer.get_x() - avg_dict['x']), 
            'y': str(accelerometer.get_y() - avg_dict['y']), 
            'z': str(accelerometer.get_z() - avg_dict['z'])}
    log.add(data)
    sleep(200)

# ========== Finished Confirmation
# Displays image to confirm logging has been halted
display.show(Image.YES)
