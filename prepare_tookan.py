import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import util

"""
    First Task is to convert the raw tookan data to something more usable
"""

# do some cool image processing on driver uploaded images

# value_counts()
# groupby().aggregate(np.sum)

def consolidate(tookan_raw):
    # get unique tookan id
    relations = pd.DataFrame(tookan_raw['Relationship'].unique(), columns=['Relationship'])
    orders = pd.DataFrame(columns=['Relationship','Team_Name','Order_ID',
                                   'Agent_Name','Vendor','Customer',
                                   'Pickup_Distance','Delivery_Distance',
                                   'Pickup_Address','Delivery_Address',
                                   'Pickup_Time_Est','Delivery_Time_Est',
                                   'Pickup_Signature_Image','Pickup_Image',
                                   'Delivery_Signature_Image','Delivery_Image',
                                   'Pickup_Started_At',
                                   'Pickup_Arrived_At','Pickup_Successful_At',
                                   'Delivery_Started_At',
                                   'Delivery_Arrived_At','Delivery_Successful_At'])
    # signature, image image added column, can we match "image_added"
    # text delivery and drop
    # caculate best of estimate of ACTUAL pickup time
    relations_p = 0
    #
    for relation in relations['Relationship']:
        mask = tookan_raw['Relationship'] == relation
        order_data = tookan_raw[mask]
        new_row = [relation]
        new_row += [order_data['Team_Name'].iloc[0]]
        new_row += [order_num_from_notes(order_data['Notes'].iloc[0])]
        new_row += [order_data['Agent_Name'].iloc[0]]
        new_row += [get_order_value(order_data, "Pick-up", "Customer_Name")]
        new_row += [get_order_value(order_data, "Delivery", "Customer_Name")]
        new_row += [get_order_value(order_data, "Pick-up", "Distance")]
        new_row += [get_order_value(order_data, "Delivery", "Distance")]
        new_row += [get_order_value(order_data, "Pick-up", "Customer_Address")]
        new_row += [get_order_value(order_data, "Delivery", "Customer_Address")]
        new_row += [get_order_value(order_data, "Pick-up", "Pick_up_Before")]
        new_row += [get_order_value(order_data, "Delivery", "Complete_Before")]
        new_row += [get_count(order_data,"Pick-up","signature_image_added")]
        new_row += [get_count(order_data,"Pick-up","image_added")]
        new_row += [get_count(order_data,"Delivery","signature_image_added")]
        new_row += [get_count(order_data,"Delivery","image_added")]
        new_row += [get_time(order_data,"Pick-up","Started at")]
        new_row += [get_time(order_data,"Pick-up","Arrived at")]
        new_row += [get_time(order_data,"Pick-up","Successful at")]
        new_row += [get_time(order_data,"Delivery","Started at")]
        new_row += [get_time(order_data,"Delivery","Arrived at")]
        new_row += [get_time(order_data,"Delivery","Successful at")]
        orders.loc[relations_p] = new_row
        relations_p += 1
    return orders


def get_order_value(order_data,type,value):
    try:
        ans = order_data[order_data['Task_Type']==type][value].iloc[0]
    except:
        ans = None
    return ans

def get_count(order_data,type,add_type):
    ans = len(order_data[(order_data['Task_Type']==type)*(order_data['Type']==add_type)])
    return ans


def get_time(order_data, type, add_type):
    mask = (order_data['Task_Type']==type)*(order_data['History_Description']==add_type)
    ans = order_data[mask]['Time']
    if ans.shape[0] > 0:
        return ans.iloc[0]
    elif add_type == "Successful at":
        mask = (order_data['Task_Type'] == type)*\
               (order_data['History_Description'] == "Status updated from Assigned to Successful")
        ans = order_data[mask]['Time']
        if ans.shape[0] > 0:
            return ans.iloc[0]
    else:
        return None


def order_num_from_notes(notes):
    # some orders have a space, # eu82d
    rec = re.compile('#\S{5,7}')
    ans = rec.search(notes)
    if ans:
        return ans.group()[1:]
    else:
        return None


def pred_add_timings(orders):
    # convert dates to datetime
    datetime_columns = ['Pickup_Started_At','Pickup_Arrived_At','Pickup_Successful_At',
                        'Delivery_Started_At','Delivery_Arrived_At','Delivery_Successful_At',
                        'Pickup_Time_Est','Delivery_Time_Est']
    for col in datetime_columns:
        orders[col] = pd.to_datetime(orders[col], '%Y-%m-%d %H:%M:%S')
    # define new columns based on time differences
    orders['time_at_vendor'] = orders['Pickup_Successful_At'] - orders['Pickup_Arrived_At']
    orders['time_to_vendor'] = orders['Pickup_Arrived_At']-orders['Pickup_Started_At']
    orders['time_for_vendor'] = orders['time_at_vendor'] + orders['time_to_vendor']
    orders['time_at_customer'] = orders['Delivery_Successful_At'] - orders['Delivery_Arrived_At']
    orders['time_to_customer'] = orders['Delivery_Arrived_At'] - orders['Delivery_Started_At']
    orders['time_for_customer'] = orders['time_at_customer'] + orders['time_to_customer']
    orders['pickup_deviation'] = orders['Pickup_Arrived_At']-orders['Pickup_Time_Est']
    orders['delivery_deviation'] = orders['Delivery_Successful_At']-orders['Delivery_Time_Est']
    orders['travel_time'] = orders['Delivery_Arrived_At']-orders['Pickup_Successful_At']
    # convert timedeltas to s
    for col in ['time_at_vendor','time_for_customer','time_to_customer','time_at_customer',
                'time_to_vendor','time_for_vendor','pickup_deviation','delivery_deviation',
                'travel_time']:
        orders[col] = orders[col].apply(lambda x: x / np.timedelta64(1,'s'))
        # apply ceiling of 4 hours for all
        orders[col] = orders[col].apply(lambda x: np.min([x,60*60*5]))
    # data must be cleaned, none should be greater than 5 hours
    # Time_At shouldn't be larger than an hour
    for col in ['time_at_vendor','time_at_customer']:
        orders[col] = orders[col].apply(lambda x: np.min([x, 60*60*1]))
    # return new time parameters
    return orders

def update_orders_address(orders):
    orders['floor'] = ''
    orders['suburb'] = ''
    orders['postal_sector'] = ''
    for i in range(0,orders.shape[0]):
        [address, country] = orders[['Delivery_Address', 'country']].iloc[i]
        tmp = extract_address_parts(address,country)
        orders.loc[i, ['postal_sector', 'suburb', 'floor']] = tmp
    return orders


def extract_address_parts(address, country):
    # convert address to list of components
    # sometimes address doesn't exist, just return None
    try:
        address_parts = [a.strip() for a in address.split(',')]
    except:
        return [None, None, None]
    # do different for HK and SG
    if country=="SG":
        floor = reg_search('(#[0-9]{2}(-?)[0-9]{2}|(Floor|Level)( )?[0-9]{1,3}|[0-9]{1,3}(/| )?F)',
                          address_parts)
        if floor != None:
            floor = reg_search('[0-9]{1,3}', [floor])
        postcode = reg_search("[0-9]{6}", address_parts)
        if postcode:
            postal_sector = postcode[:2]
        else:
            postal_sector = None
        suburb = None
        # postal district from online..
    elif country=="HK":
        floor = reg_search('(#[0-9]{2}(-?)[0-9]{2}|(Floor|Level)( )?[0-9]{1,3}|[0-9]{1,3}(/| )?F)',
                          address_parts)
        if floor != None:
            floor = reg_search('[0-9]{1,3}', [floor])
        suburb = replace_parts(1, address_parts, 1)
        postal_sector = None
    else:
        postal_sector = None
        suburb = None
        floor = None
    return [postal_sector,suburb,floor]

"""
Replace unnecessary parts of address, country, so that scan 
doesn't catch it
"""
def replace_parts(pattern, address_parts, back=0):
    if back == 1:
        address_parts = reversed(address_parts)
    for part in address_parts:
        if reg_search('[0-9]',[part]) == None and part.find('Hong Kong')==-1 and part.find('HK')==-1:
            return part
    return None

"""
Perform a regex search
"""
def reg_search(pattern,address_parts,back=0):
    compiled = re.compile(pattern)
    if back == 1:
        address_parts = reversed(address_parts)
    for part in address_parts:
        found = compiled.search(part)
        if found:
            return found.group()
    return None


def get_country(team_name):
    country = team_name[:2]
    if country == "SG" or country == "HK":
        return country
    else:
        return None

def get_country2(phone):
    if re.match("$(\+?)852",phone) != None:
        return "HK"
    elif re.match("$(\+?)65",phone) != None:
        return "SG"
    else:
        return None

def pred_add_country(orders):
    # get from Team Name otherwise go for +852 / +65 in phones
    orders['country'] = orders['Team_Name'].apply(get_country)
    return orders

def get_seconds(time):
    try:
        return time / np.timedelta64(1, 's')
    except:
        return None


# vendor postal address should matter too
def plot_data(orders):
    plotD = orders['delivery_deviation']
    plotD.apply(lambda x: x/60).plot(kind='hist',bins=500)
    plt.show()

def update_orders():
    """
    Ideal pramaters:
    dependent
    - variance from prediction
    - time at vendor
    - time at customer
    independent
    - vendor
    - time at vendor/customer
    - vendor/customer postal area, suburb, street, building
    - vendor/customer floor
    Eventually...
    - team/agent name
    - customer (extra buffer for special customers)
    :return:
    """
    tookan_raw = pd.read_csv('tookan/tookan_raw.csv',encoding='ISO-8859-1')
    # convert multiline tookan data to one entry per order
    orders = consolidate(tookan_raw)
    # add timings for sections using driver sign ins
    orders = pred_add_timings(orders)
    # add country of order
    orders = pred_add_country(orders)
    # update address to ensure it has country (for Google API)
    orders = update_orders_address(orders)
    print(orders.shape[0])
    orders_length = [orders.shape[0], None]
    orders.to_csv('tookan/orders_dirty.csv')
    # change some vendor namings
    orders = fix_vendor_namings(orders)
    # remove rows that contain nans to improve data quality
    orders = remove_nans(orders)
    print(str(orders.shape[0])+"  remove nans")
    # remove timings which are probably incorrectly input
    orders = remove_bad_timings(orders)
    print(str(orders.shape[0])+"  remove bad timings")
    orders_length[1] = orders.shape[0]
    # print(str(orders_length[0])+" -> "+str(orders_length[1]))
    # save data to a csv for use
    orders.to_csv('tookan/orders.csv')


#update_orders()

# abc is seperated when it shouldn't be


def remove_nans(orders):
    # drop columns with na values
    na_drop_cols = ['Pickup_Address', 'Delivery_Address', 'Pickup_Started_At',
                    'Pickup_Arrived_At', 'Pickup_Successful_At', 'Delivery_Started_At',
                    'Delivery_Arrived_At', 'Delivery_Successful_At', 'Customer', 'Vendor', 'country']
    orders.dropna(subset=na_drop_cols, inplace=True)
    return orders


def remove_bad_timings(orders):
    # remove rows when the data has less than 0 timings
    # don't look at for timings as they will be fixed via their parts
    time_min = 30       # seconds
    time_max = 3*60*60  # seconds
    time_cols = ['time_at_vendor', 'time_to_vendor',
                 'time_at_customer', 'time_to_customer']
    for col in time_cols:
        orders = orders[orders[col] >= time_min]
    for col in time_cols:
        orders = orders[orders[col] <= time_max]
    return orders

def fix_vendor_namings(orders):
    orders.replace('Artisan Boulangerie Co.', 'Artisan Boulangerie Co', inplace=True)
    return orders


# update_orders()