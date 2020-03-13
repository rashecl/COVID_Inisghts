# COVID_Inisghts

# To extract JHU dataset:
from COVID.extract import JHU
countriesDF = JHU.getCountryDF()
statesDF = JHU.getStateDF()

# Then you can start playing with the data
from matplotlib import pyplot as plt
plt.plot(statesDF['CA'].time, statesDF['CA'].confirmed)
plt.show()

