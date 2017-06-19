import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date

orders = pd.read_csv('tookan/orders.csv',encoding='ISO-8859-1')

plt.figure()

# get top 10 vendors
top_vendors = orders.Vendor.value_counts().head(5).index.tolist()
# look at time spend at vendors
plt.figure()
orders[orders.Vendor.isin(top_vendors)].boxplot('time_at_vendor',by='Vendor')

plt.show()

# histogram
# timings = all october, yesterday, day before
# get date
orders['date'] = orders.Pickup_Time_Est.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
# define october
oct_start = date.today().replace(2016,10,1)
oct_end = date.today().replace(2016,10,31)

ans = orders[(orders.date>=oct_start)*(orders.date<=oct_end)].delivery_deviation.apply(lambda x: x/60)
print(ans.describe())
ans.plot(kind='hist')
plt.show()


# vendor postal address should matter too
def plot_data(orders):
    plotD = orders['delivery_deviation']
    plotD.apply(lambda x: x/60).plot(kind='hist',bins=500)
    plt.show()
