"""
Script to plot the results using pandas.
Vendor postal address?
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date


def plot_time_spent_at_vendors(orders, count):
    """
    Create plot of time spent at vendors.
    :param orders:
    :param count: number of vendors to return
    :return:
    """
    # plot time spent at vendor for top vendors
    plt.figure()
    # get top 5 vendors
    top_vendors = orders.Vendor.value_counts().head(count).index.tolist()
    orders[orders.Vendor.isin(top_vendors)].boxplot('time_at_vendor', by='Vendor')
    plt.show()
    return

def plot_delivery_deviation(orders, month):
    """
    Plot a histogram of delivery deviation (lateness) for
    a given month.
    :param orders:
    :param month: (int) month number
    :return:
    """
    plt.figure()
    # timings = all october, yesterday, day before
    # convert dates to datetime
    orders['date'] = orders.Pickup_Time_Est.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
    # define start and end
    start = date.today().replace(2016, month, 1)
    end = date.today().replace(2016, month, 31)

    select_orders = orders[(orders.date >= start)*(orders.date <= end)].delivery_deviation.apply(lambda x: x/60)
    print(select_orders.describe())
    select_orders.plot(kind='hist')
    plt.show()
    return


def plot_delivery_deviation(orders):
    plt.figure()
    orders['delivery_deviation'].apply(lambda x: x/60).plot(kind='hist',bins=500)
    plt.show()
    return


orders = pd.read_csv('tookan/orders.csv', encoding='ISO-8859-1')


