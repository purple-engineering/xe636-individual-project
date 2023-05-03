# Description: A program that takes the file containing the acceleration data computes the delta time between data collections and converts acceleration to velocity and displacement counterparts. The data should then be plotted on an appropriate graph.
# Author: Sonny Rickwood
# Version: 20230307-1122

# ========== Library Imports
from matplotlib import pyplot as plt

# ========== Global Variable Declaration
running_time, dlt_time, norm_running_time = [], [0], [0] # List declaration to store running time, delta time  and normalised running time

acceleration_dict = {'x':[0], 'y':[0], 'z':[0]}
velocity_dict = {'x':[0], 'y':[0], 'z':[0]}
distance_dict = {'x':[0], 'y':[0], 'z':[0]}
# Dictionary declaration for storing lists of acceleration, velocity and distance values

# ========== Function Declaration
def calculations(acceleration, delta_time, previous_velocity, previous_distance):
    # Global function for converting acceleration data to velocity and displacement counterparts
    # acceleration, previous_velocity and previous_distance to be entered as list of x, y, z
    # delta_time can be number value

    
    # Lambda declarations for converting single value acceleration data to velocity and displacement
    velocity_calc = lambda a, t, pv: round(((a * t) + pv), 3)
    distance_calc = lambda a, t, pv, pd: round((((a * (t**2))/2) + (pv * t) + (pd)), 3)
    
    # Local list declaration for containing calculated values
    lcl_vel_vctr, lcl_dis_vctr = [], [] 
    
    for index, accel in enumerate(acceleration):
        # Loop for iterating over the acceleration data,
        # calculating velocity and displacement counterparts
        # and appending value to local list counterparts
        lcl_vel_vctr.append(velocity_calc(accel, delta_time, previous_velocity[index]))
        lcl_dis_vctr.append(distance_calc(accel, delta_time, previous_velocity[index], previous_distance[index]))
        
    return lcl_vel_vctr, lcl_dis_vctr


def accel_norm(milliG, weighting):
    # Global function for converting milliG value to meters per second
    # with weighting feature to removed data below a certain value
    
    # Lambda function for convertion
    calc = lambda mG: (mG/1024) * 9.80665
    
    milliG =  float(milliG)
    
    if (milliG > weighting) or (milliG < -weighting):
        return calc(milliG)
    else:
        return 0

# ========== Main Program 
if __name__ == '__main__':
    # ========== File Work
    try:
        # Attempt to open outlined file and go over the contents to obtain:
            # Running time
            # Acceleration data pre-converted to meters per second
        with open('microbit.csv', 'r') as file:
            # Opens file and assigns the contents to variable file
            # This ensures the file will be closed if an error or forgetting to do so
            for index, line in enumerate(file):
                # Iterate ovet each line of the files contents
                # Where their is a comma, split the data to individual entries of a list
                # Remove '\n' is present
                logged_data = line.strip('\n').split(',')
                 
                if index != 0:
                    # First line of every file contains the headers of the logged data so this needs to be skipped over
                    # If not on the first line, the contents of the line is appended to their repsetive dictionary/list
                    # Assigns the current time to a global variable to be used for working out the delta time between values
                    current_time = float(logged_data[0])
                    running_time.append(current_time)
                    
                    acceleration_dict['x'].append(accel_norm(logged_data[1], 20))
                    acceleration_dict['y'].append(accel_norm(logged_data[2], 10))
                    acceleration_dict['z'].append(accel_norm(logged_data[3], 50))
                                       
                    if index > 1:
                        # Skips over the second line as their is no delta time for the first data collection
                        # Delta time is worked out by getting the current time and minusing the previously stored running time
                        dlt_time.append(round(current_time - running_time[-2], 3))           
    except Exception as e:
        print(e)
    
    # ========== Delta Time Calculations
    dlt_time[0] = round(sum(dlt_time[1:]) / len(dlt_time[1:]), 3)
    # The delta time list must match the length of the acceleration data.
    # But one value is unknown. To approximate it, the average of all the delta time is taken

    # ========== Running Time Normalisation
    for index, time in enumerate(dlt_time):
        # The running time of the Microbit will not be zerod so needs to be normalised
        # Delta time is iterated over with the sum being coverted at each step.
        # The sum is then appended to a list for each iterationg to calculate the normalised running time.
        norm_running_time.append(round(norm_running_time[index] + time, 3))
    
    dlt_time.insert(0, 0) # Inserts additional value to ensure same length list as acceleration data
    
    # ========== Velocity & Distance Calculations
    for index, time in enumerate(norm_running_time):
        if index != 0:
            # Iterates over every acceleration value to calculate the velocity and displacement values
            # Local lists are declared to store the previous values required for the calculations
            accel_vctr = [acceleration_dict['x'][index], acceleration_dict['y'][index], acceleration_dict['z'][index]]
            prev_vel_vctr = [velocity_dict['x'][index - 1], velocity_dict['y'][index - 1], velocity_dict['z'][index - 1]]
            prev_dis_vctr = [distance_dict['x'][index - 1], distance_dict['y'][index - 1], distance_dict['z'][index - 1]]
            
            vel_vctr, dis_vctr = calculations(accel_vctr, dlt_time[index], prev_vel_vctr, prev_dis_vctr)
            
            print(dlt_time[index], accel_vctr[0], vel_vctr[0], dis_vctr[0]) # Prints values for debugging
            
            velocity_dict['x'].append(vel_vctr[0])
            velocity_dict['y'].append(vel_vctr[1])
            velocity_dict['z'].append(vel_vctr[2])
            
            distance_dict['x'].append(dis_vctr[0])
            distance_dict['y'].append(dis_vctr[1])
            distance_dict['z'].append(dis_vctr[2])
    
    # ========== Plotting Data
    fig, plots = plt.subplots(3, 1, figsize=(6, 6))
    # Create a figure that two variables can reference. Fig for the overall figure, plots for a list of each subplot.

    fig.subplots_adjust(left=0.125, bottom=0.1, right=0.98, top=0.97, hspace=0.1)
    # Adjust the margins/paddings of the subplots to ensure they are not overlapping
    
    font_title = {'family':'serif', 'color':'black', 'size':12, 'weight':'bold'}
    font_axis = {'family':'serif', 'color':'black', 'size':10}
    # Create a dictionary for font references to easily change values

    axis = ['x', 'y', 'z']
    titles = ['Acceleration','Velocity','Distance']
    ylabels = ['Acceleration [ms^-2]','Velocity [ms^-1]','Distance [m]']
    # Declaring lists so when the plots are being iterated over the accelerometer values, titles and ylabels can be easily referenced 
    
    for index, dim in enumerate(axis):
        # Iterating over the accelerometer axis and plotting the axis being iterated over on their respective subplot
        plots[0].step(norm_running_time, acceleration_dict[dim], label=dim)
        plots[1].plot(norm_running_time, velocity_dict[dim], label=dim)
        plots[2].plot(norm_running_time, distance_dict[dim], label=dim)
        
    
    plots[0].set_xticklabels("")
    plots[1].set_xticklabels("")
    plots[2].set_xlabel('Time [s]', fontdict = font_axis)
    plots[2].legend(fontsize=10, ncol=3, loc="lower left")
    
    for index, plot in enumerate(plots):
        # Iterate over each subplot and assign their respective attributes  from the previous declared dictionaries and lists
        lcl_title = "{} vs. Time Graph".format(titles[index])
        
        plot.set_ylabel(ylabels[index], fontdict = font_axis)
        
        plot.set_xbound(min(norm_running_time), max(norm_running_time))
        
        plot.grid()
    
    plt.show()    
    
    # plt.savefig('MicrobitAcceleration.png', dpi=300)
    # Save the figure in the same folder as the code. 
    # Commented out for testing purposes