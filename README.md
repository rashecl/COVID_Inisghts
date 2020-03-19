# COVID_Insights
Currently you can see the number of cases in each state if you run US_coronavirus_map.py.
(You would have to install bokeh.) 

I also started creating a package for our projects.<br>

# To extract JHU dataset:
from COVID.extract import JHU <br>
countriesDF = JHU.getCountryDF() <br>
statesDF = JHU.getStateDF() <br>

# Then you can start playing with the data
from matplotlib import pyplot as plt <br>
plt.plot(statesDF['CA'].time, statesDF['CA'].confirmed) <br>
plt.show()<br>

# Other resources:
https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6
https://covidtracking.com/
https://covidly.com/
https://nextstrain.org/ncov?m=div

