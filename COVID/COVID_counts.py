import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
from os import path
# Obtain data from NYT or CT (COVID Tracking project):
def getDailyCountyData(src='NYT'):
    if src == 'NYT':
        NYT_counties_daily = pd.read_csv(
            'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
        NYT_counties_daily['date'] = NYT_counties_daily['date'].apply(lambda x: pd.to_datetime(x).date())
        NYT_counties_daily = NYT_counties_daily.drop(columns=['fips'])
        NYT_counties_daily.columns = ['date', 'county', 'state', 'positive', 'death']
        NYT_counties_daily['source'] = ['NYT'] * len(NYT_counties_daily)
        NYT_counties_daily['stateName'] = NYT_counties_daily['state']
        from bokeh.sampledata.us_states import data as stateBorders
        stateDict = {stateBorders[k]['name']: k for k in list(stateBorders.keys())}
        NYT_counties_daily['state'] = NYT_counties_daily['state'].apply(
            lambda x: stateDict[x] if x in stateDict.keys() else 'XX')

        positiveIncrease = np.array([])
        deathIncrease = np.array([])
        allIdxs = np.array([])
        for state in NYT_counties_daily.state.unique():
            for county in NYT_counties_daily[NYT_counties_daily['state'] == state].county.unique():
                idxs = np.where((NYT_counties_daily['state'] == state) & (NYT_counties_daily['county'] == county))[0]
                positiveIncrease = np.append(positiveIncrease,
                                             np.diff(np.insert(NYT_counties_daily.iloc[idxs]['positive'].values, 0, 0)))
                deathIncrease = np.append(deathIncrease,
                                          np.diff(np.insert(NYT_counties_daily.iloc[idxs]['death'].values, 0, 0)))
                allIdxs = np.append(allIdxs, idxs)
        NYT_counties_daily = pd.concat([NYT_counties_daily,
                                        pd.Series(positiveIncrease, name='positiveIncrease', index=allIdxs),
                                        pd.Series(deathIncrease, name='deathIncrease', index=allIdxs)], axis=1)


        return NYT_counties_daily
    elif src == 'CT':
        raise ValueError('County data not available from COVID Tracker')
        return
    else:
        raise ValueError('Unknown source: ' + src)
    return

def getDailyStateData(src='CT'):
    """
    Retrieve daily state data from specified source.
    src can be 'CT' for COVID tracking project
    or 'NYT' for The New York Times.
    CT has testing data as well as hospital data over shorter intervals.
    NYT has cases and deaths spanning a longer interval.
    """
    if src == 'CT':
        CT_states_daily = pd.read_csv('http://covidtracking.com/api/states/daily.csv')
        to_date = lambda x: pd.to_datetime(str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8]).date()
        CT_states_daily['date'] = CT_states_daily['date'].apply(to_date)
        CT_states_daily = CT_states_daily.drop(columns=['hash', 'dateChecked', 'fips'])
        CT_states_daily = CT_states_daily.sort_values('date').reset_index()
        CT_states_daily['source'] = ['CT'] * len(CT_states_daily)
        from bokeh.sampledata.us_states import data as stateBorders
        stateDict = {k: stateBorders[k]['name'] for k in list(stateBorders.keys())}
        CT_states_daily['stateName'] = CT_states_daily['state'].apply(
            lambda x: stateDict[x] if x in stateDict.keys() else 'XX')
        return CT_states_daily
    elif src == 'NYT':
        NYT_states_daily = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
        NYT_states_daily['date'] = NYT_states_daily['date'].apply(lambda x: pd.to_datetime(x).date())
        NYT_states_daily = NYT_states_daily.drop(columns=['fips'])
        NYT_states_daily.columns = ['date', 'state', 'positive', 'death']
        NYT_states_daily['source'] = ['NYT'] * len(NYT_states_daily)
        # Change the state names to abbreviations
        NYT_states_daily['stateName'] = NYT_states_daily['state']
        from bokeh.sampledata.us_states import data as stateBorders
        stateDict = {stateBorders[k]['name']: k for k in list(stateBorders.keys())}
        NYT_states_daily['state'] = NYT_states_daily['state'].apply(
            lambda x: stateDict[x] if x in stateDict.keys() else 'XX')
        # Add positive and death increases
        allIdxs = np.array([])
        positiveIncrease = np.array([])
        deathIncrease = np.array([])
        for state in NYT_states_daily.state.unique():
            idxs = np.where(NYT_states_daily['state'] == state)[0]
            positiveIncrease = np.append(positiveIncrease,
                                         np.diff(np.insert(NYT_states_daily.iloc[idxs]['positive'].values, 0, 0)))
            deathIncrease = np.append(deathIncrease,
                                      np.diff(np.insert(NYT_states_daily.iloc[idxs]['death'].values, 0, 0)))
            allIdxs = np.append(allIdxs, idxs)
        NYT_states_daily = pd.concat([NYT_states_daily,
                                      pd.Series(positiveIncrease, name='positiveIncrease', index=allIdxs),
                                      pd.Series(deathIncrease, name='deathIncrease', index=allIdxs)], axis=1)
        return NYT_states_daily
    else:
        raise ValueError('Unknown source: ' + src)
    return

def getDailyUSData(src='CT'):
    if src == 'CT':
        to_date = lambda x: pd.to_datetime(str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8]).date()
        CT_US_daily = pd.read_csv('https://covidtracking.com/api/us/daily.csv')
        CT_US_daily['date'] = CT_US_daily['date'].apply(to_date)
        CT_US_daily = CT_US_daily.drop(columns=['states', 'hash', 'dateChecked'])
        CT_US_daily = CT_US_daily.sort_values('date').reset_index(drop=True)
        CT_US_daily['source'] = ['CT'] * len(CT_US_daily)
        return CT_US_daily
    elif src == 'NYT':
        NYT_states_daily = getDailyStateData(src='NYT')
        NYT_US_daily = NYT_states_daily.groupby('date').sum()
        NYT_US_daily['source'] = ['NYT'] * len(NYT_US_daily)
        NYT_US_daily = NYT_US_daily.reset_index()
        return NYT_US_daily
    else:
        raise ValueError('Unknown source: ' + src)
    return

full_filePath = path.join(path.dirname(__file__), 'regionPopulations.p')

[usPopulation, statePopulations, countyPopulations, cityPopulations] = pickle.load(open(full_filePath, "rb"))

def appendTestingDeathRates(df):
    mp = 1e5 # multiplier (i.e rates expressed in per 100,000)
    testing = False
    if 'totalTestResults' in df.columns:
        testing = True
    if 'county' in df.columns:
        geo_level ='county'
    elif 'state' in df.columns:
        geo_level ='state'
    else:
        geo_level ='US'

    print(geo_level)
    print(testing)

    deathRate=[]
    positiveRate=[]
    testingRate=[]

    for idx in range(len(df)):
        # Get population
        if geo_level == 'county':
            state = df['state'].iloc[idx]
            if state == 'XX':
                deathRate.append(np.nan)
                positiveRate.append(np.nan)
                testingRate.append(np.nan)
                continue
            else:
                pass
            if df['county'].iloc[idx] in list(countyPopulations[state].keys()):
                pop = countyPopulations[state][df['county'].iloc[idx]]
            elif df['county'].iloc[idx] in list(cityPopulations.query("state == '" + state + "'")['city']):
                city = df['county'].iloc[idx]
                pop = cityPopulations.query("city == '" + city + "'")['population']

        elif geo_level == 'state':
            state = df['state'].iloc[idx]
            if state not in list(statePopulations.keys()):
                deathRate.append(np.nan)
                positiveRate.append(np.nan)
                testingRate.append(np.nan)
                continue
            else:
                pass
            pop = statePopulations[state]
        elif geo_level == 'US':
            pop = usPopulation

        deathRate.append(df.iloc[idx,:].death*mp/pop)
        positiveRate.append(df.iloc[idx,:].positive*mp/pop)
        if testing == True:
            testingRate.append(df.iloc[idx,:].totalTestResults*mp/pop)

    df["deathRate"]=deathRate
    df["positiveRate"]=positiveRate
    if testing == True:
        df["testingRate"]=testingRate
    return df


try:
    full_filePath = path.join(path.dirname(__file__), 'CovidCounts.p')
    [countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated] = pickle.load(open(full_filePath, "rb"))
except:
    lastUpdated = datetime.now() - timedelta(days=1)

if (datetime.now() - lastUpdated).total_seconds()/3600 > 4:
    countyDF = appendTestingDeathRates(getDailyCountyData(src='NYT'))
    stateDF_NYT = appendTestingDeathRates(getDailyStateData(src='NYT'))
    stateDF_CT = appendTestingDeathRates(getDailyStateData(src='CT'))
    usDF_NYT = appendTestingDeathRates(getDailyUSData(src='NYT'))
    usDF_CT = appendTestingDeathRates(getDailyUSData(src='CT'))

    lastUpdated = datetime.now()
    full_filePath = path.join(path.dirname(__file__), 'CovidCounts.p')
    pickle.dump([countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated], open(full_filePath, "wb"))
else:
    pass

print('Finished getting latest COVID counts.')

# [countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT] = pickle.load(open("./COVID/extract/CovidCounts.p", "rb"))

# [countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated] = pickle.load(open("./COVID/extract/CovidCounts.p", "rb"))