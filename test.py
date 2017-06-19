#
import pandas as pd
import numpy as np
import delivery_time
from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt
#
#
def run_test():
    # open orders csv
    orders = pd.read_csv('tookan/orders.csv', encoding="ISO-8859-1")
    sample_rate = 10
    orders = get_data_correct(orders)
    # get sample of data to test and train
    orders_test = pd.DataFrame(orders.sample(frac=1/sample_rate, random_state=2016))
    orders_train = pd.DataFrame(orders[~orders.Relationship.isin(orders_test.Relationship)])
    # get required data for input from orders_test
    # prepare_test_data(orders_test)
    # get delivery time from assigned picjup
    res = pd.DataFrame(orders_test['Relationship'])
    res['delivery_time_performance'] = orders_test['Delivery_Successful_At'] - orders_test['Pickup_Time_Est']
    #res = pd.DataFrame(orders_test['Delivery_Successful_At'] - orders_test['Pickup_Time_Est'],
    #                   columns=['delivery_time_performance'])
    # actual delivery time
    res['delivery_time_actual'] = orders_test['Delivery_Successful_At']-orders_test['Pickup_Started_At']
    # get caterspot predictions
    res['delivery_time_caterspot'] = orders_test['Delivery_Time_Est'] - \
                                     orders_test['Pickup_Time_Est']
    # convert columns to seconds
    second_columns = ['delivery_time_performance', 'delivery_time_actual',
                      'delivery_time_caterspot']
    for col in second_columns:
        res[col] = res[col].apply(lambda x: get_seconds(x))

    # calculate pickup times using the model
    ans = predict_test()
    # convert answers to delivery time
    # res now contains 3 columns, old, act, pred
    # compare these to calculate lateness
    # visual is good
    #res = pd.concat([res, ans['delivery_time']], axis=0, ignore_index=True)
    res.reset_index(inplace=True)
    #res = pd.concat([res, ans['delivery_time']], axis=0)
    # positive is early, negative is late
    res['variation_new'] = ans['delivery_time'] - res['delivery_time_performance']
    res['variation_old'] = res['delivery_time_caterspot']-res['delivery_time_performance']
    # plot
    print(res['variation_new'].apply(lambda x: x/60).describe())
    print(res['variation_old'].apply(lambda x: x/60).describe())
    try:
        print("OLD Results on time/late:," + str(sum(res['variation_old']>0))+" - "+str(sum(res['variation_old']<0)))
        print("NEW Results on time/late:," + str(sum(res['variation_new']>0))+" - "+str(sum(res['variation_new']<0)))
        print("OLD Results less than 5/1 min late:," + str(sum(res['variation_old']>-300))+" - "+str(sum(res['variation_old']>-60)))
        print("NEW Results less than 5/1 min late:," + str(sum(res['variation_new']>-300))+" - "+str(sum(res['variation_new']>-60)))
    except:
        otuh = 1
    # plt.figure()
    #res['variation_new'].apply(lambda x:x/60).plot(kind='box')
    #res['variation_new'].apply(lambda x:x/60).plot(kind='box')
    plt.figure()
    plt.boxplot([res['variation_old'].apply(lambda x:x/60),
                 res['variation_new'].apply(lambda x:x/60)],
                widths=0.3, positions=[0.4, 0.8])
    #res['variation_old'].apply(lambda x:x/60).plot(kind='box')
    res.to_csv('tookan/test_results.csv')
    plt.show()
    # Done! ...compare statisctics...


def date_to_today(date):
    today = datetime.today()
    date = date.replace(day=today.day,month=today.month,year=today.year)
    return date


def get_time(date):
    return date.second + date.minute*60 + date.hour+60*60


def get_data_correct(orders):
    # convert to datetime...
    cols_to_datetime = ['Delivery_Successful_At', 'Pickup_Arrived_At',
                        'Pickup_Time_Est','Delivery_Time_Est','Pickup_Started_At']
    for col in cols_to_datetime:
        orders[col] = orders[col].apply(lambda x: convert_to_datetime(x))
    return orders

def convert_to_datetime(date_string):
    try:
        return datetime.strptime(date_string,'%Y-%m-%d %H:%M:%S')
    except:
        try:
            return datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
        except:
            return None

def prepare_test_data(orders_test):
    input = orders_test[['Order_ID', 'Pickup_Address', 'Delivery_Address', 'Delivery_Time_Est',
                         'Vendor','Team_Name']]
    input['Country'] = input['Team_Name'].apply(lambda x: x[0:2])
    input.drop('Team_Name', axis=1, inplace=True)
    input['New_Delivery_Time_Est'] = None
    # must convert all Delivery_Time_Est to the future
    for i in range(0, input.shape[0]):
        date = input['Delivery_Time_Est'].iloc[i]
        today = datetime.today()
        weekday_mod = today.weekday()-date.weekday()+7
        new_date = today + timedelta(days=weekday_mod)
        new_date = new_date.replace(hour=date.hour,minute=date.minute,second=date.second,
                         microsecond=date.microsecond)
        input['New_Delivery_Time_Est'].iloc[i] = new_date.strftime('%m/%d/%Y %H:%M:%S')
    input['Delivery_Time_Est'] = input['New_Delivery_Time_Est']
    input = input.drop(['New_Delivery_Time_Est'],axis=1)
    # input ready, save to csv
    input.to_csv('tookan/test.csv', index=False)

def predict_test():
    # extract answers to output.csv
    delivery_time.csv_input('tookan/test.csv')
    # pick those up
    ans = pd.read_csv('input/output.csv', encoding='ISO-8859-1')
    ans['Departure_Time'] = ans['Departure_Time'].apply(lambda x: convert_to_datetime(x))
    ans['Delivery_Time_Est'] = ans['Delivery_Time_Est'].apply(lambda x: convert_to_datetime(x))
    ans['delivery_time'] = ans['Delivery_Time_Est']-ans['Departure_Time']
    ans['delivery_time'] = ans['delivery_time'].apply(lambda x: get_seconds(x))
    return ans

def get_seconds(time):
    try:
        return time / np.timedelta64(1, 's')
    except:
        return None

run_test()