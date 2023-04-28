# ===== Library imports ====================
from microbit import *
import radio, log, speech

# ===== Microbit Configuration ====================
accelerometer.set_range(8) # Range: 0-8, Default: 8
global_radio_group = 255 # Range: 0-255, Default: 255
radio.config(group=global_radio_group, power=7)
radio.on()

# ===== Start Procedure ====================
message = radio.receive()

while message != "Confirm Launch":
    # Loop to check if the radio received the message "Confirm Launch"
    # Alternatively, if button A is pressed, the radio will send "Confirm Launch" and break the loop
    message = radio.receive()
    if button_a.was_pressed():
        radio.send("Confirm Launch")
        break
    display.show(Image.NO)

# ===== Start Confirmation ====================
display.show(Image.NO.invert()) # Inverts the image on the display to show the button or radio signal has been acknowledged
radio.off() # Turns radio off to save power
log.delete(True) # Remove all contents within the Microbits memory
set_volume(255)

# ===== Accelerometer Calibration ====================
# Set up calibration dictionary and loop variables
cali_dict = {'x':0, 'y':0, 'z':0, 'len':0}
wait_len, slp_len, last_time = 10000, 100, 0
# wait_len: Duration of the loop (ms)
# slp_len: Pauses between each iteration (ms)
# last_time: Used to ensure the correct number is displayed on the Microbit display

while wait_len > 0:
    # Creates a loop of duration wait_len/slp_len
    # In Each iteration, the accelerometer value is added to its respective dictionary entry
    # The calibration length is also increased by one for each iteration
    
    accel_x, accel_y, accel_z = accelerometer.get_values()
    
    cali_dict['x'] += accel_x
    cali_dict['y'] += accel_y
    cali_dict['z'] += accel_z
    
    cali_dict['len'] += 1
    wait_len -= slp_len

    time = wait_len // 1000 # Floor divided the remaining time by 1000 to give the number of whole seconds left in the loop
    
    if last_time != time:
        # Checks to see if the last recorded time is different from the number of whole seconds left
        # If it is different, then the last_time is replaced, the time is spoken, and the display is changed
        speech.say(str(time))
        last_time = time
        display.show(Image.ALL_CLOCKS[time])
    
    sleep(slp_len)

# Dictionary to store the average accelerometer bias
avg_dict = {'x':cali_dict['x']/cali_dict['len'], 
            'y':cali_dict['y']/cali_dict['len'], 
            'z':cali_dict['z']/cali_dict['len']}

# ===== Start Logging Confirmation ====================
for x in range(0, 3):
    # Flashes the display three times to confirm to the user that the calibration process is complete and data logging is commencing
    display.show(Image.SQUARE)
    sleep(100)
    display.show(Image.SQUARE.invert())
    sleep(100)
    speech.say('Go')

# ===== Data logging ====================
display.show(Image.HAPPY)
while not(button_b.was_pressed()):
    # Continually logs the accelerometer values minus their bias until button B is pressed
    # A 200ms delay is present between logs to ensure the Microbits memory does not fill up too quickly
    data = {'x': str(accelerometer.get_x() - avg_dict['x']), 
            'y': str(accelerometer.get_y() - avg_dict['y']), 
            'z': str(accelerometer.get_z() - avg_dict['z'])}
    log.add(data)
    sleep(200)

# ===== End Confirmation ====================
display.show(Image.YES)
