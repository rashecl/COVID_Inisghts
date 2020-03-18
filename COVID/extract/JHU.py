"""
This package can be used to extract data from the JHU Coronavirus Resource Center:
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data
"""
import pandas as pd
import numpy as np
import matplotlib.path as mpltPath
from COVID import us_map
import pickle

import matplotlib.pyplot as plt
urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv']

def getCountriesDF(confirmed = pd.read_csv(urls[0]), recovered = pd.read_csv(urls[1]), deaths = pd.read_csv(urls[2])):
    time = pd.to_datetime(list(deaths.columns[4::]))
    df =pd.DataFrame()
    for country in confirmed['Country/Region'].unique():
        confirmed_t = np.sum(confirmed[confirmed['Country/Region'] == country].iloc[:, 4:])
        recovered_t = np.sum(recovered[recovered['Country/Region'] == country].iloc[:, 4:])
        deaths_t = np.sum(deaths[deaths['Country/Region'] == country].iloc[:, 4:])
        if np.any([np.isnan(confirmed_t[-1]), np.isnan(recovered_t[-1]), np.isnan(deaths_t[-1])]):
            lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)]) - 1
        else:
            lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)])
        df = pd.concat([df, pd.DataFrame(
            {country: {'confirmed': confirmed_t[:lastIdx],
                       'recovered': recovered_t[:lastIdx],
                       'deaths': deaths_t[:lastIdx],
                       'time': time[:lastIdx]}})], axis=1)
    return df

# Note: This is continental US
state_names = ['Nevada', 'Arizona', 'Wisconsin', 'Georgia', 'Kansas', 'Connecticut', 'Indiana', 'Maine',
     'Massachusetts', 'Montana', 'Maryland', 'Arkansas', 'Alabama', 'Virginia', 'Nebraska', 'Kentucky',
     'New York', 'Colorado', 'Vermont', 'South Dakota', 'Michigan', 'Missouri', 'North Carolina',
     'Rhode Island', 'Idaho', 'Delaware', 'District of Columbia', 'New Hampshire', 'Minnesota',
     'North Dakota', 'Oklahoma', 'Iowa', 'Tennessee', 'Florida', 'Louisiana', 'New Mexico',
     'Wyoming', 'Pennsylvania', 'South Carolina', 'Utah', 'West Virginia', 'Washington',
     'Mississippi', 'Oregon', 'Illinois', 'New  Jersey', 'California', 'Ohio', 'Texas']

state_abbrevs = ['NV', 'AZ', 'WI', 'GA', 'KS', 'CT', 'IN', 'ME', 'MA', 'MT', 'MD', 'AR',
    'AL', 'VA', 'NE', 'KY', 'NY','CO', 'VT', 'SD', 'MI', 'MO', 'NC', 'RI', 'ID', 'DE', 'DC',
    'NH', 'MN', 'ND', 'OK', 'IA', 'TN', 'FL', 'LA', 'NM', 'WY', 'PA', 'SC', 'UT', 'WV', 'WA',
    'MS', 'OR', 'IL', 'NJ', 'CA', 'OH', 'TX']

def getUS_DF(url):
    rawDF = pd.read_csv(url)
    rawDF = rawDF.loc[rawDF['Country/Region'] == 'US']
    rawDF.index = range(len(rawDF))
    return rawDF

confirmed = getUS_DF(urls[0])
recovered = getUS_DF(urls[1])
deaths = getUS_DF(urls[2])
time = pd.to_datetime(list(deaths.columns[4::]))

countyBorders = us_map.countyBorders
# [coord_countykeys] = pickle.load(open("coord_countykeys.p", "rb"))
[coord_countykeys] = pickle.load(open("./COVID/extract/coord_countykeys.p", "rb"))

def getCounty(lon, lat, state):
    global coord_countykeys
    if (lon,lat) in coord_countykeys.keys():
        return coord_countykeys[(lon,lat)]
    point = [lon, lat]
    stateCounties = countyBorders[countyBorders.state == state]
    for c, county in enumerate(stateCounties.county_name.unique()):
        # check to see if the point is possibly in the the limits of the county
        if lon >= np.min(stateCounties.iloc[c, :].lons) and lon <= np.max(
                stateCounties.iloc[c, :].lons) and lat >= np.min(
                stateCounties.iloc[c, :].lats) and lat <= np.max(stateCounties.iloc[c, :].lats):
            polygon = [[stateCounties.iloc[c, :].lons[i], stateCounties.iloc[c, :].lats[i]] for i in
                       range(len(stateCounties.iloc[c, :].lons))]
            if mpltPath.Path(polygon).contains_point(point):
                coord_countykeys.update({(lon,lat):county})
                return county
        else:
            continue
    return ' '

def getState_RegionalDF(confirmed = confirmed, recovered = recovered , deaths = deaths, time = time):
    """
    Obtain dataframe of state and regional data extracted from the JHU Coronavirus resource center:
    https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data

    e.g.: df = getState_RegionalDF()
    df.columns == ['state', 'state_name', 'location', 'Lat', 'Long', 'confirmed', 'recovered', 'deaths', 'time']
    """
    df = pd.DataFrame(columns = ['state', 'state_name','location', 'Lat', 'Long', 'confirmed', 'recovered', 'deaths', 'time'])
    for idx in range(len(deaths)): # we'll assume that deaths, confirmed, and recovered are the same dimensions
        if deaths.iloc[idx, 0] == 'Washington, D.C.':
            continue
        loc = deaths.iloc[idx, 0].split(', ')
        if loc[0] == 'District of Columbia':
            state_name = loc[0]
            state_idx = state_names.index(loc[0])
            state = state_abbrevs[state_idx]
            confirmed_t = confirmed.iloc[idx, 4:len(time)+3].ravel()
            recovered_t = recovered.iloc[idx, 4:len(time)+3].ravel()
            deaths_t = deaths.iloc[idx, 4:len(time)+3].ravel()
            if np.any([np.isnan(confirmed_t[-1]), np.isnan(recovered_t[-1]), np.isnan(deaths_t[-1])]):
                lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)]) - 1
            else:
                lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)])
            df = df.append({'state': state,
                            'state_name': state_name,
                            'location': state_name,
                            'Lat': deaths['Lat'][idx],
                            'Long': deaths['Long'][idx],
                            'confirmed': confirmed_t[:lastIdx],
                            'recovered': recovered_t[:lastIdx],
                            'deaths': deaths_t[:lastIdx],
                            'time': time[:lastIdx]}, ignore_index=True)
        elif len(loc) == 2: # This occurs when we're talking about a region in a state
            if loc[1] in state_abbrevs:
                state_idx = state_abbrevs.index(loc[1])
                state_name = state_names[state_idx]
                state = state_abbrevs[state_idx]
                confirmed_t = confirmed.iloc[idx, 4:len(time)+3].ravel()
                recovered_t = recovered.iloc[idx, 4:len(time)+3].ravel()
                deaths_t = deaths.iloc[idx, 4:len(time)+3].ravel()
                location_name = loc[0] #loc[0].split(' ')[:-1][0] if loc[0].split(' ')[-1] == 'County' else loc[0]
                if np.any([np.isnan(confirmed_t[-1]), np.isnan(recovered_t[-1]), np.isnan(deaths_t[-1])]):
                    lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)]) - 1
                else:
                    lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)])
                df = df.append({'state': state,
                                'state_name': state_name,
                                'location': location_name,
                                'Lat': deaths['Lat'][idx],
                                'Long': deaths['Long'][idx],
                                'confirmed': confirmed_t[:lastIdx],
                                'recovered': recovered_t[:lastIdx],
                                'deaths': deaths_t[:lastIdx],
                                'time': time[:lastIdx]}, ignore_index=True)
        elif len(loc) == 1:
            if loc[0] in state_names:
                state_name = loc[0]
                state_idx = state_names.index(loc[0])
                state = state_abbrevs[state_idx]
                confirmed_t = confirmed.iloc[idx, 4:len(time)+3].ravel()
                recovered_t = recovered.iloc[idx, 4:len(time)+3].ravel()
                deaths_t = deaths.iloc[idx, 4:len(time)+3].ravel()
                if np.any([np.isnan(confirmed_t[-1]), np.isnan(recovered_t[-1]), np.isnan(deaths_t[-1])]):
                    lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)]) - 1
                else:
                    lastIdx = np.min([len(confirmed_t), len(recovered_t), len(deaths_t)])
                df = df.append({'state': state,
                                'state_name': state_name,
                                'location': ' ',
                                'Lat': deaths['Lat'][idx],
                                'Long': deaths['Long'][idx],
                                'confirmed': confirmed_t[:lastIdx],
                                'recovered': recovered_t[:lastIdx],
                                'deaths': deaths_t[:lastIdx],
                                'time': time[:lastIdx]}, ignore_index=True)
    #
    county_names = []
    for idx in range(len(df)):
        if df['location'][idx].isspace():
            county_names.append(' ')
        else:
            lon = df['Long'][idx]
            lat = df['Lat'][idx]
            state = df['state'][idx]
            county_names.append(getCounty(lon, lat, state))

    df = pd.concat([df, pd.DataFrame(county_names, columns=['county_name'])], axis=1)
    pickle.dump([coord_countykeys], open("./COVID/extract/coord_countykeys.p", "wb"))
    # pickle.dump([coord_countykeys], open("coord_countykeys.p", "wb"))
    return df

def getCountiesDF(states_regionsDF = getState_RegionalDF()):
    df = pd.DataFrame(columns= ['state', 'state_name', 'county_name', 'confirmed', 'recovered', 'deaths', 'time'])
    for state in states_regionsDF['state'].unique():
        state_name = state_names[state_abbrevs.index(state)]
        stateDF = states_regionsDF[states_regionsDF['state'] == state]
        for county in stateDF.county_name.unique():
            if county.isspace():
                continue
            confirmed_t = np.sum(stateDF[stateDF['county_name'] == county]['confirmed'], axis=0)
            recovered_t = np.sum(stateDF[stateDF['county_name'] == county]['recovered'], axis=0)
            deaths_t = np.sum(stateDF[stateDF['county_name'] == county]['deaths'], axis=0)
            df = df.append({'state': state,
                       'state_name': state_name,
                       'county_name': county,
                       'confirmed': confirmed_t,
                       'recovered': recovered_t,
                       'deaths': deaths_t,
                       'time': time}, ignore_index=True)
    return df

def mergeStatesDF(states_regionsDF = getState_RegionalDF(), time = time):
    df = pd.DataFrame()
    for idx, state in enumerate(state_abbrevs):
        if state in states_regionsDF.state.unique():
            state_name = state_names[idx]

            confirmed_t = np.sum(states_regionsDF[states_regionsDF['state'] == state]['confirmed'], axis=0)
            recovered_t = np.sum(states_regionsDF[states_regionsDF['state'] == state]['recovered'], axis=0)
            deaths_t = np.sum(states_regionsDF[states_regionsDF['state'] == state]['deaths'], axis=0)
            df = pd.concat([df, pd.DataFrame({state: {'state_name': state_name,
                            'confirmed': confirmed_t,
                            'recovered': recovered_t,
                            'deaths': deaths_t,
                            'time': time}})],
                           axis=1)
    return df


def getStateDF():
    """
    Obtain data frame of state level data extracted from the JHU Coronavirus resource center:
    https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data

    e.g.: df = getStateDF()
    df.columns == ['NV', 'AZ', 'WI', 'GA', 'KS', 'CT', 'IN', 'ME', 'MA', 'MT', 'MD', 'AR',
       'AL', 'VA', 'NE', 'KY', 'NY', 'CO', 'VT', 'SD', 'MI', 'MO', 'NC', 'RI',
       'ID', 'DE', 'D.C.', 'NH', 'MN', 'ND', 'OK', 'IA', 'TN', 'FL', 'LA',
       'NM', 'WY', 'PA', 'SC', 'UT', 'WV', 'WA', 'MS', 'OR', 'IL', 'NJ', 'CA',
       'OH', 'TX']

   df['NV'] ==  confirmed     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...
                deaths        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...
                recovered     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...
                state_name                                               Nevada
                time          DatetimeIndex(['2020-01-22', '2020-01-23', '20...
    """
    df = mergeStatesDF()
    return df
