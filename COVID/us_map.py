from bokeh.sampledata.us_states import data as stateBorders
from bokeh.sampledata.us_counties import data as counties
from COVID.extract import COVID_counts
import pandas as pd
import numpy as np
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


state_names = ['Nevada', 'Arizona', 'Wisconsin', 'Georgia', 'Kansas', 'Connecticut', 'Indiana', 'Maine',
     'Massachusetts', 'Montana', 'Maryland', 'Arkansas', 'Alabama', 'Virginia', 'Nebraska', 'Kentucky',
     'New York', 'Colorado', 'Vermont', 'South Dakota', 'Michigan', 'Missouri', 'North Carolina',
     'Rhode Island', 'Idaho', 'Delaware', 'Washington, D.C.', 'New Hampshire', 'Minnesota',
     'North Dakota', 'Oklahoma', 'Iowa', 'Tennessee', 'Florida', 'Louisiana', 'New Mexico',
     'Wyoming', 'Pennsylvania', 'South Carolina', 'Utah', 'West Virginia', 'Washington',
     'Mississippi', 'Oregon', 'Illinois', 'New Jersey', 'California', 'Ohio', 'Texas', 'Alaska', 'Hawaii']

state_abbrevs = ['NV', 'AZ', 'WI', 'GA', 'KS', 'CT', 'IN', 'ME', 'MA', 'MT', 'MD', 'AR',
    'AL', 'VA', 'NE', 'KY', 'NY','CO', 'VT', 'SD', 'MI', 'MO', 'NC', 'RI', 'ID', 'DE', 'DC',
    'NH', 'MN', 'ND', 'OK', 'IA', 'TN', 'FL', 'LA', 'NM', 'WY', 'PA', 'SC', 'UT', 'WV', 'WA',
    'MS', 'OR', 'IL', 'NJ', 'CA', 'OH', 'TX', 'AK', 'HI']

df = pd.read_csv("https://coronadatascraper.com/data.csv")
# Select US data, rows with population, strip county
df = df.query("country == 'United States'")[['state', 'county', 'population']]
df['county'] = df['county'].drop(3925)
df['county'] = df['county'].apply(lambda x: x.replace("County", "").strip() if type(x) == str else np.nan)
df['population'] = df['population'].apply(lambda x: float(x))
df = df.reset_index(drop=True)
df = df.drop(list(np.where(df.population.isnull() | df.population.isna() | df.state.isna())[0]))
df = df.reset_index(drop=True)
statePopulations = df[df.county.isna()].reset_index(drop=True).drop(columns='county')
statePopulations['state'] = statePopulations['state'].replace(dict(zip(state_names, state_abbrevs)))
usPopulation = statePopulations.population.sum()

statePopulations=dict(zip(statePopulations.state,statePopulations.population))


countyPopulations=df[~df.county.isna()].reset_index(drop=True)
countyPopulations['state'] = countyPopulations['state'].replace(dict(zip(state_names, state_abbrevs)))
countyPopulationsDict = {}
for state in state_abbrevs:
    countyDict={}
    for county in countyPopulations[countyPopulations['state']==state].county.unique():
        countyDict.update({county: \
                           countyPopulations[(countyPopulations['state']==state) & (countyPopulations['county']==county)].population.values[0]})
        
    countyPopulationsDict.update({state : countyDict})
countyPopulations=countyPopulationsDict


pickle.dump([usPopulation, statePopulations, countyPopulations], open("./extract/regionPopulations.p", "wb"))

