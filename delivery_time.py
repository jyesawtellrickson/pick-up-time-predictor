import googlemaps
import pandas as pd
from datetime import datetime
from datetime import timedelta
import numpy as np
import math
import point_to_point
import tookan_analysis
import util

disp_lan = 'en-GB' #'zh-CN'


"""
Delivery time will be assumed to be made up from three sections
    1. Pickup
    2. Point-to-point
    3. Drop off

Driver should be sent a one-pager for the delivery, outlining all the information he will need.

order size should matter!

Level = > 5 < 20 = + 3 mins
Order Size
=> Subtotal / $10-$60 = people
1. Carry < 25 = 0
2. Trolley > 25  + 3 mins
3. LOTS	> 50 + 5 mins (Set-up)


"""
"""
    predict function to predict the delivery time for a certain delivery.
    As inputs, requires location for pick-up and drop-off as well as the
    required delivery time.

    Potential inclusions could be the order type\size

"""


def predict_departure(pick_location, drop_location, drop_time_s, vendor, country, order_value):
    # convert drop_time from a string to a proper datetime object
    # drop_time = datetime.strptime(drop_time_s, '%I:%M %p %d %b %Y')
    drop_time = datetime.strptime(drop_time_s, '%m/%d/%Y %H:%M:%S')
    # Calculate the three different parts of delivery time
    part_1 = tookan_analysis.pred_pickup_time(vendor, order_value)
    #part_2 = point_to_point.point_to_point(pick_location, drop_location, drop_time, country)  # traffic in 0
    part_2 = [10*60, 15*60]
    part_3 = tookan_analysis.pred_delivery_time(drop_location, country, drop_time, order_value)
    if part_2 == None:
        print("Address couldn't be found")
        return "Address couldn't be found"
    # calculate delivery time with and without traffic
    delivery_time = (part_1 + part_2[1] + part_3)/60
    delivery_time += 3  # 4.2
    ##### ALways increment HK orders because it's HK #####
    if country == "HK":
        delivery_time += 1
    if part_2[0] == None:
        print("Note - traffic NOT included")
    # convert drop_time from a string to a proper datetime object
    drop_time = datetime.strptime(drop_time_s, '%m/%d/%Y %H:%M:%S')
    # drop_time = datetime.strptime(drop_time_s, '%I:%M %p %d %b %Y')
    #
    mins = timedelta(seconds=60)
    # round departure time to nearest 5 minutes
    #delivery_time_r = math.ceil(delivery_time/5)*5
    delivery_time_r = round(delivery_time/5)*5
    #
    act_dep = drop_time - delivery_time_r*mins
    # time taken for the door to door driving.
    show_res = 1
    if show_res == 1:
        print("To deliver to the customer by ", drop_time)
        print("The driver should arrive at the vendor by ", act_dep)
        print("The estimated travel time is: {0:.0f} minutes.".format(part_2[0]/60))
        print("Time at vendor is: {0:.0f} minutes".format(part_1/60))
        print("Time at customer is: {0:.0f} minutes".format(part_3/60))

    return act_dep

"------------------------------------------------------------------------"




def csv_input(input_file='input/input.csv'):
    """
    Take csv as input with: pickup address, delivery address, time, vendor, country and maybe order_value.
    """
    csv_in = pd.read_csv(input_file, encoding='ISO-8859-1')
    if csv_in.shape[1] == 6:
        csv_in['Order_Value'] = None
    csv_in['Departure_Time'] = None
    # for each row, run calcs
    for i in range(0, csv_in.shape[0]):
        funin = csv_in.ix[i, :].tolist()
        # make sure addresses have country
        funin = add_country_to_funin(funin)
        print(funin[0])
        order_value = None
        est = predict_departure(funin[1], funin[2], funin[3], funin[4], funin[5], funin[6])
        csv_in['Departure_Time'].iloc[i] = est
    csv_in.to_csv('input/output.csv')
    return


def add_country_to_funin(funin):
    funin[1] = util.add_country(funin[1], funin[5])
    funin[2] = util.add_country(funin[2], funin[5])
    return funin

# disable when doing test
# csv_input()