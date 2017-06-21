# Pick-up Time Predictor
Scripts to predict the pick-up time for on-time delivery in the F&B industry.

The estimate breaks down the time into three sections:
1. Pick-up time
2. Travel time
3. Drop-off time

## Pick-up Time
When a driver arrives at a destination, he is required to find a park, pick up the food and make it back to the car. Potential issues include:
- no park
  Harder with restaurants with central location
  Use type=restaurant and postcode={central}
- tricky building access
  Restaurants will tend to be in a good location, no worries
  Caterers may be slightly more difficult. Use average for nearby.
  Do we want to know how long this leg takes
- food not ready
  Check with the caterer day of, to check food will be ready on time.
  How often is this a problem?
- something missing from order (and unprepared)
  Driver should check order on arrival.
  If problem INSTANTLY let customer know, tag on tookan which flags to Calvin
- no plates/cutlery/other
  Do we want to provide, possibly branded
  Driver could pick up from central store
  Survey the deliveries.

## Travel Time

Point-to-point
Once the driver is back in the car, he must drive to the end destination.
He may also go via another address, but this is currently out of scope.
Potential issues include:
- heavy traffic: use google maps predictions
- gets lost: driver is sent directions by logistics company, or by us, from Gmaps
- bad weather: should know in advance and be able to plan around
        program in leeway for bad weather, check historicals
        use weather reports from api and add in 10%
- accident: re-route, message
- events: should know in advance and be able to plan around

If significant delay, > 10 minutes en route, alert customer.
All the above should be covered by gmaps but we may need to program in our own leeway.

Duration in traffic can only be estimated when the departure time is set.
First run with arrival time set, take resultant duration, multiply by 1.2,
and subtract from arrival time to get departure time. Rerun, and take away
duration from arrival time.

## Drop-off Time
Once a driver arrives, he must find a park, get the food to the right floor
and get sign-off from the customer. Potential issues include:
- building car park has height restrictions
- building has no car park
- no street park available
- building security an issue
- customer on high floor, tricky location
- customer not happy with the food
- food in bad condition
- customer has no cutlery/plates
- postal code matters because of parking

Solutions:
Call office ahead of time and ask for entry instructions, send to driver
Call building management for key offices

## Contributions

Things I want to do:
- Linear regressor for pickup/dropoff, convert categorical variables to dichotomous dummy variables. May want to first use clustering on the categorical variables (e.g. caterers) to improve the functionality of the model.
- Use more address parts in calculating drop-off time, e.g. street, not just suburb.
- Do some cool image processing on driver uploaded images on Tookan
