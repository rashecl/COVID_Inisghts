# COVID_Inisghts

# To extract JHU dataset:
from COVID.extract import JHU <br>
countriesDF = JHU.getCountryDF() <br>
statesDF = JHU.getStateDF() <br>

# Then you can start playing with the data
from matplotlib import pyplot as plt <br>
plt.plot(statesDF['CA'].time, statesDF['CA'].confirmed) <br>
plt.show()<br>

