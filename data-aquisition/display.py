# Title: Microbit Accelerometer Display Program
# Description: Program for opening Microbit CSV logged acceleration 
# data and displaying it to the user
# Author: Sonny Rickwood
# Version: 230307-1122-SR

# ========== Library Imports =========================================
from matplotlib import pyplot as plt

# ========== Global Variable Declaration =============================
running_time, dlt_time, norm_running_time = [], [0], [0]
# Lists for storing Microbits running time, delta time and normalised
# running time

acceleration_dict = {'x':[0], 'y':[0], 'z':[0]}
velocity_dict = {'x':[0], 'y':[0], 'z':[0]}
distance_dict = {'x':[0], 'y':[0], 'z':[0]}
# Dictionaries for storing acceleration, velocity & distance values
# in lists

# ========== Function Declaration ====================================
def calculations(acceleration, delta_time, previous_velocity, previous_distance):
    # Function for converting the acceleration values into velocity
    # and distance values
    # acceleration, previous_velocity and previous_distance should be
    # given as a three part list in the form x, y, z
    
    def velocity_calc(a, t, pv): 
        # Takes an individual index from the lists inputted into the 
        # main function and calculates the relative velocity value
        # rounded to 3 decimal points
        return round(((a * t) + pv), 3)
    
    def distance_calc(a, t, pv, pd): 
        # Takes an individual index from the lists inputted into the 
        # main function and calculates the relative distance value 
        # rounded to 3 decimal points
        return round((((a * (t**2))/2) + (pv * t) + (pd)), 3)
    
    
    lcl_vel_vctr, lcl_dis_vctr = [], [] 
    # Local lists for velocity and distance vectors in the 
    # form x, y, z
    
    for index, accel in enumerate(acceleration):
        # Loop for iterating over the acceleration list and carrying 
        # out the velocity & distance calculation on each index 
        # value. Then appending each calculated value to a local list
        lcl_vel_vctr.append(velocity_calc(accel, 
                                          delta_time, 
                                          previous_velocity[index]))
        
        lcl_dis_vctr.append(distance_calc(accel, 
                                          delta_time, 
                                          previous_velocity[index], 
                                          previous_distance[index]))
    
    return lcl_vel_vctr, lcl_dis_vctr

# ========== Lambda Declaration =====================================

def accel_norm(milliG, weighting):
    calc = lambda mG: (mG/1024) * 9.80665
    
    milliG =  float(milliG)
    
    if (milliG > weighting) or (milliG < -weighting):
        return calc(milliG)
    else:
        return 0
# Function for converting the acceleration values to meters per second squared

# ========== Main Program =========================================
if __name__ == '__main__':
    # ========== File Work ===========================================
    try:
        with open('microbit.csv', 'r') as file:
            # Open and read the declared file and later refer to it
            # as 'file.'
            for index, line in enumerate(file):
                # Iterate over each line of the opened file. Where 
                # here is a comma split each line into individual 
                # indexes of a local list called logged_data. A check 
                # is also conducted to remove the special character 
                # \n if it is present
                logged_data = line.strip('\n').split(',')
                 
                if index != 0:
                    # Checks to make sure the current line being 
                    # iterated is not the first line of the file. The 
                    # first line of the file contains the titles of 
                    # the logged data and if not skipped over, would 
                    # cause an error to be thrown.
                    current_time = float(logged_data[0])
                    running_time.append(current_time)
                    # Gets the value stored in index 0 of the
                    # logged_data list and stores it in the local 
                    # variable  current_time. Then the value is 
                    # appended to the running_time list
                    
                    acceleration_dict['x'].append(accel_norm(logged_data[1], 20))
                    acceleration_dict['y'].append(accel_norm(logged_data[2], 10))
                    acceleration_dict['z'].append(accel_norm(logged_data[3], 50))
                    
                    # Appends the remaining logged_data values to their 
                    # respective dictionary lists after they have been 
                    # passed through the acceleration normalisation function
                                       
                    if index > 1:
                        # Checks to make sure the file has had one 
                        # pass-through of the logged data and if it has, 
                        # then compute the difference between the previous 
                        # running time and the current. This value is then 
                        # rounded to 3 decimal places
                        dlt_time.append(round(current_time - running_time[-2], 3))           
    except Exception as e:
        print(e)
    
    # ========== Delta Time Calculations & Normalisation ===================
    dlt_time[0] = round(sum(dlt_time[1:]) / len(dlt_time[1:]), 3)
    # Converts the zeroth index of the dlt_time list to an average of all 
    # the values excluding the first value

    for index, time in enumerate(dlt_time):
        # Iterates over the dlt_time list, adds the current iteration to the 
        # values of the previous iteration and 
        # then appends this to the norm_running_time list
        norm_running_time.append(round(norm_running_time[index] + time, 3))
    
    dlt_time.insert(0, 0)
    # Inserts the value 0 at the beginning of the dlt_time list
    
    # ========== Velocity & Distance Calculations ===========================
    for index, time in enumerate(norm_running_time):
        
        if index != 0:
            # Iterates over every value of the norm_running_time list apart 
            # from index 0. During the iteration, it gets the respective 
            # iterations acceleration values and the previous iterations 
            # velocity and distance values. They are then stored in their 
            # respective vectors. Each vector is then passed into the 
            # calculations function with the current iterations dlt_time for 
            # two lists to be returned of the calculated velocity and 
            # distance values. The values are then appended to their 
            # respective lists in the velocity and distance dictionaries
            
            
            
            accel_vctr = [acceleration_dict['x'][index], 
                          acceleration_dict['y'][index], 
                          acceleration_dict['z'][index]]
            prev_vel_vctr = [velocity_dict['x'][index - 1], 
                             velocity_dict['y'][index - 1], 
                             velocity_dict['z'][index - 1]]
            prev_dis_vctr = [distance_dict['x'][index - 1], 
                             distance_dict['y'][index - 1], 
                             distance_dict['z'][index - 1]]
            
            vel_vctr, dis_vctr = calculations(accel_vctr, 
                                              dlt_time[index], 
                                              prev_vel_vctr, prev_dis_vctr)
            
            print(dlt_time[index], accel_vctr[0], vel_vctr[0], dis_vctr[0])
            
            velocity_dict['x'].append(vel_vctr[0])
            velocity_dict['y'].append(vel_vctr[1])
            velocity_dict['z'].append(vel_vctr[2])
            
            distance_dict['x'].append(dis_vctr[0])
            distance_dict['y'].append(dis_vctr[1])
            distance_dict['z'].append(dis_vctr[2])
    
    # ========== Plotting Data ========================================
    fig, plots = plt.subplots(3, 1, figsize=(6, 6))
    # Create a figure that two variables can reference. Fig for the overall 
    # figure, plots for a list of each subplot.

    fig.subplots_adjust(left=0.125, bottom=0.1, right=0.98, top=0.97, hspace=0.1)
    # Adjust the margins/paddings of the subplots to ensure they are not 
    # overlapping
    
    font_title = {'family':'serif', 'color':'black', 'size':12, 'weight':'bold'}
    font_axis = {'family':'serif', 'color':'black', 'size':10}
    # Create a dictionary for font references to easily change values

    axis = ['x', 'y', 'z']
    titles = ['Acceleration','Velocity','Distance']
    ylabels = ['Acceleration [ms^-2]','Velocity [ms^-1]','Distance [m]']
    # Declaring lists so when the plots are being iterated over the 
    # accelerometer values, titles and ylabels can be easily referenced 
    
    for index, dim in enumerate(axis):
        # Iterating over the accelerometer axis and plotting the axis being 
        # iterated over on their respective subplot
        plots[0].step(norm_running_time, acceleration_dict[dim], label=dim)
        plots[1].plot(norm_running_time, velocity_dict[dim], label=dim)
        plots[2].plot(norm_running_time, distance_dict[dim], label=dim)
        
    
    plots[0].set_xticklabels("")
    plots[1].set_xticklabels("")
    plots[2].set_xlabel('Time [s]', fontdict = font_axis)
    plots[2].legend(fontsize=10, ncol=3, loc="lower left")
    
    for index, plot in enumerate(plots):
        # Iterate over each subplot and assign their respective attributes 
        # from the previous declared dictionaries and lists
        lcl_title = "{} vs. Time Graph".format(titles[index])
        
        plot.set_ylabel(ylabels[index], fontdict = font_axis)
        
        plot.set_xbound(min(norm_running_time), max(norm_running_time))
        
        plot.grid()
    
    plt.show()    
    
    #plt.savefig('MicrobitAcceleration.png', dpi=300)
    # Save the figure in the same folder as the code. 
    # Commented out by default for testing purposes