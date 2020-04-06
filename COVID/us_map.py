from bokeh.sampledata.us_states import data as stateBorders
from bokeh.sampledata.us_counties import data as counties
import pandas as pd
import pickle

# stateBorders['D.C.'] = stateBorders.pop('DC')
stateBorders= pd.DataFrame(stateBorders)  # This contains boundaries for each state
# excludeStates = ['AK', 'HI'] # Exclude the states
stateBorders = stateBorders.drop(columns=['AK', 'HI'])

countyBorders = pd.DataFrame(columns = ['county', 'state', 'lats', 'lons'])
for code, county in counties.items():
    # county_name = county['detailed name'].split(', ')[0]
    county_name = county['name']
    state=county['state'].upper()
    lats=county['lats']
    lons=county['lons']
    countyBorders = countyBorders.append({'county': county_name,
                    'state': state,
                    'lats': lats,
                    'lons': lons}, ignore_index=True)

pickle.dump([stateBorders, countyBorders], open("./extract/regionBorders.p", "wb"))