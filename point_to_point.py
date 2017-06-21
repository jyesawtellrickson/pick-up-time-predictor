import googlemaps
import pandas as pd
from datetime import datetime
from datetime import timedelta
import numpy as np
import math

import credentials

disp_lan = 'en-GB' #'zh-CN'

"""
    predict function to predict the delivery time for a certain delivery.
    As inputs, requires location for pick-up and drop-off as well as the
    required delivery time.

    Potential inclusions could be the order type\size
"""

def get_client():
    """
    Connect to Google Client.
    :return:
    """
    gClient = googlemaps.Client(key=credentials.gkey)
    return gClient


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
