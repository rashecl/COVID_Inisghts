import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle

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


try:
    [countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated] = pickle.load(open("./COVID/extract/CovidCounts.p", "rb"))
except:
    lastUpdated = datetime.now() - timedelta(days=1)

if (datetime.now() - lastUpdated).total_seconds()/3600 > 4:
    countyDF = getDailyCountyData(src='NYT')
    stateDF_NYT = getDailyStateData(src='NYT')
    stateDF_CT = getDailyStateData(src='CT')
    usDF_NYT = getDailyUSData(src='NYT')
    usDF_CT = getDailyUSData(src='CT')
    lastUpdated = datetime.now()
    pickle.dump([countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated], open("./COVID/extract/CovidCounts.p", "wb"))
else:
    pass

# [countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT] = pickle.load(open("./COVID/extract/CovidCounts.p", "rb"))

# [countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated] = pickle.load(open("./COVID/extract/CovidCounts.p", "rb"))