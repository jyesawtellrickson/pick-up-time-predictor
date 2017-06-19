import googlemaps
import pandas as pd
from datetime import datetime
from datetime import timedelta
import numpy as np
import math

disp_lan = 'en-GB' #'zh-CN'

"""
    predict function to predict the delivery time for a certain delivery.
    As inputs, requires location for pick-up and drop-off as well as the
    required delivery time.

    Potential inclusions could be the order type\size
"""

def get_client():

    # gkey = 'AIzaSyDB1Tz_MYTxELf7uoWIusUUIydJxBLvYqU'
    gkey = 'AIzaSyAorsEg2RHfw66iBGXA8ulamM21Gj2gNEY'  # jye's key
    gClient = googlemaps.Client(key=gkey)

    return gClient

"""
--2--
Point-to-point
Once the driver is back in the car, he must drive to the end destination.
He may also go via another address, but this is currently out of scope.
Potential issues include:
    - heavy traffic
        use google maps predictions
    - gets lost
        driver is sent directions by logistics company, or by us, from Gmaps
    - bad weather
        should know in advance and be able to plan around
        program in leeway for bad weather, check historicals
        use weather reports from api and add in 10%
    - accident
        re-route, message
    - events
        should know in advance and be able to plan around

If significant delay, > 10 minutes en route, alert customer.
All the above should be covered by gmaps but we may need to program in our own leeway.

Duration in traffic can only be estimated when the departure time is set.
First run with arrival time set, take resultant duration, multiply by 1.2,
and subtract from arrival time to get departure time. Rerun, and take away
duration from arrival time.

"""

def point_to_point(location1, location2, arr_time, country):

    gmaps = get_client()

    params = {'mode': 'driving', # walking/bicycling could be useful
              'alternatives': False,
              'avoid': 'tolls',
              'language': disp_lan,
              'units': 'metric',
              'region': country}

    # Avoid, waypoints,
    try:
        directions_result = gmaps.directions(location1,
                                             location2,
                                             arrival_time=arr_time,
                                             **params)
    except:
        return None
    # directions_result is a list and dict structure
    dir_dict = directions_result[0]

    #if dir_dict['warnings'] != []:
    #    print('warnings raised:', dir_dict['warnings'])

    est_dur = dir_dict['legs'][0]['duration']['value']
    params['traffic_model'] = 'pessimistic'  # best_guess
    # estimate departure time
    secs = timedelta(seconds=1)
    est_dep = arr_time - est_dur*secs*1.3
    # rerun with departure time
    directions_result = gmaps.directions(location1,
                                         location2,
                                         departure_time=est_dep,
                                         **params)

    dir_dict = directions_result[0]
    # duration in traffic won't show if too far in the future
    # conditional statement or try statement
    mod = 1
    act_dur = dir_dict['legs'][0]['duration']['value']*mod
    try:
        act_dur_t = dir_dict['legs'][0]['duration_in_traffic']['value']*mod
    except KeyError:
        act_dur_t = None
    return [act_dur_t, act_dur]
