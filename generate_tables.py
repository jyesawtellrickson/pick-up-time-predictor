import googlemaps
import pandas as pd
from datetime import datetime
from datetime import timedelta
import numpy as np
import math
import point_to_point
import tookan_analysis

disp_lan = 'en-GB' #'zh-CN'



"--------------------------------------------------------------------------"
"""
    Function to update Table 1 with new location information.
    This information can then be later queried for any location
    based predictions.
"""
# keys: bounds, summary, waypoint order, overview polyline, copyrights, legs, warnings
def update_table_1(location):

    hk_loc = [22.2855200, 114.1576900]
    place_params = {'language': disp_lan,
                    'type': 'address',
                    'location': hk_loc,  # will need this to change for other locations
                    'radius': 40*1000
                    }

    gmaps = get_client()
    # do I want to use autocomplete to find the place originally?
    # or do we assume user has it covered...
    place_actual = googlemaps.places.places(gmaps, location, **place_params)
    place_id = place_actual['results'][0]['place_id']
    # get detailed results
    # if smart, could avoid querying this by checking id now
    place_detail = googlemaps.places.place(gmaps, place_id, language=disp_lan)

    address_dict = {}
    # create dictionary of parts with type and long name
    for part in place_detail['result']['address_components']:
        # print(part['types'], ":", part['long_name'])
        address_dict[part['types'][0]] = part['long_name']
    # CAREFUL this assumes that the part description is the first value but this might not always be true
    # and what about the other part 'political', do we want that too?

    # import table
    table_1 = pd.read_pickle('table_1.pkl')

    # Next step is to add this location to the table (if not already there)
    if place_id not in table_1.index:
        # go ahead and add data
        new_add = []
        # convert address_dict to list that will fit into table_1
        for col in table_1.columns:
            if col in address_dict.keys():
                new_add = new_add + [address_dict[col]]
            else:
                new_add = new_add + [np.nan]

        table_1.loc[place_id] = new_add

    # save updated file
    table_1.to_pickle('table_1.pkl')

    return

"""
    Function to generate table 1 for the first time.
    List of table headings taken direct from google api website.
    https://developers.google.com/places/supported_types#table1
"""
def generate_table_1():

    table_1 = pd.DataFrame(columns=['administrative_area_level_1', 'administrative_area_level_2',
                                    'administrative_area_level_3', 'administrative_area_level_4',
                                    'administrative_area_level_5', 'colloquial_area','country','establishment',
                                    'finance','floor','food','general_contractor','geocode','health',
                                    'intersection','locality','natural_feature','neighborhood',
                                    'place_of_worship','political','point_of_interest','post_box',
                                    'postal_code','postal_code_prefix','postal_code_suffix','postal_town',
                                    'premise','room','route','street_address','street_number','sublocality',
                                    'sublocality_level_4','sublocality_level_5','sublocality_level_3',
                                    'sublocality_level_2','sublocality_level_1','subpremise'],
                           )
    table_1.index.name = 'place_id'
    table_1.to_pickle('table_1.pkl')

    return

def generate_table_2():

    table_2 = pd.DataFrame(columns=['pick_place_id','drop_place_id', 'drop_time',
                                    'delivery_size','delivery_type','delivery_cost']
                           )

    table_2.index.name = 'delivery_id'
    table_2.to_pickle('table_2.pkl')

    return

def generate_table_3():

    table_3 = pd.DataFrame(columns=['actual_time', 'predicted_time', 'problem', 'comments'])

    table_3.index.name = 'delivery_id'
    table_3.to_piclke('table_3.pkl')

"""
    Function to generate all tables.
"""
def generate_all_table():

    generate_table_1()
    generate_table_2()
    generate_table_3()

    return

