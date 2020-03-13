"""
This package can be used to extract data from the JHU Coronavirus Resource Center:
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv']

def getCountryDF(confirmed = pd.read_csv(urls[0]), recovered = pd.read_csv(urls[1]), deaths = pd.read_csv(urls[2])):
    time = pd.to_datetime(list(deaths.columns[4::]))
    df =pd.DataFrame()
    for country in confirmed['Country/Region'].unique():
        df = pd.concat([df, pd.DataFrame({country: {'confirmed': np.sum(confirmed[confirmed['Country/Region'] == country].iloc[:,4:]),
                                                  'recovered': np.sum(recovered[recovered['Country/Region'] == country].iloc[:,4:]),
                                                  'deaths': np.sum(deaths[deaths['Country/Region'] == country].iloc[:,4:]),
                                                  'time': time}})], axis=1)
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
    'AL', 'VA', 'NE', 'KY', 'NY','CO', 'VT', 'SD', 'MI', 'MO', 'NC', 'RI', 'ID', 'DE', 'D.C.',
    'NH', 'MN', 'ND', 'OK', 'IA', 'TN', 'FL', 'LA', 'NM', 'WY', 'PA', 'SC', 'UT', 'WV', 'WA',
    'MS', 'OR', 'IL', 'NJ', 'CA', 'OH', 'TX']

def getUS_DF(url):
    rawDF = pd.read_csv(url)
    rawDF = rawDF.loc[rawDF['Country/Region'] == 'US',:]
    rawDF.index = range(len(rawDF))
    return rawDF

confirmed = getUS_DF(urls[0])
recovered = getUS_DF(urls[1])
deaths = getUS_DF(urls[2])
time = pd.to_datetime(list(deaths.columns[4::]))

def getState_RegionalDF(confirmed = confirmed, recovered = recovered , deaths = deaths, time = time):
    """
    Obtain dataframe of state and regional data extracted from the JHU Coronavirus resource center:
    https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data

    e.g.: df = getState_RegionalDF()
    df.columns == ['state', 'state_name', 'location', 'Lat', 'Long', 'confirmed', 'recovered', 'deaths', 'time']
    """
    df = pd.DataFrame(columns = ['state', 'state_name','location', 'Lat', 'Long', 'confirmed', 'recovered', 'deaths', 'time'])
    for idx in range(len(deaths)): # we'll assume that deaths, confirmed, and recovered are the same dimensions
        loc = deaths.iloc[idx, 0].split(', ')
        if len(loc) == 2: # This occurs when we're talking about a region in a state
            if loc[1] in state_abbrevs:
                state_idx = state_abbrevs.index(loc[1])
                state_name = state_names[state_idx]
                state = state_abbrevs[state_idx]
                if state == 'AL':
                    print(idx)
                confirmed_t = np.reshape(np.array(confirmed.iloc[idx, 4::]),(-1))
                recovered_t = np.reshape(np.array(recovered.iloc[idx, 4::]), (-1))
                deaths_t = np.reshape(np.array(deaths.iloc[idx, 4::]), (-1))
                location_name = loc[0].split(' ')[:-1] if loc[0].split(' ')[-1] == 'County' else loc[0]
                df = df.append({'state': state,
                                'state_name': state_name,
                                'location': location_name,
                                'Lat': deaths['Lat'][idx],
                                'Long': deaths['Long'][idx],
                                'confirmed': confirmed_t,
                                'recovered': recovered_t,
                                'deaths': deaths_t,
                                'time': time}, ignore_index=True)
        elif len(loc) == 1:
            if loc[0] in state_names:
                state_name = loc[0]
                state_idx = state_names.index(loc[0])
                state = state_abbrevs[state_idx]
                confirmed_t = np.reshape(np.array(confirmed.iloc[idx, 4::]),(-1))
                recovered_t = np.reshape(np.array(recovered.iloc[idx, 4::]), (-1))
                deaths_t = np.reshape(np.array(deaths.iloc[idx, 4::]), (-1))
                df = df.append({'state': state,
                                'state_name': state_name,
                                'location': np.nan,
                                'Lat': deaths['Lat'][idx],
                                'Long': deaths['Long'][idx],
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
