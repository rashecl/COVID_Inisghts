import matplotlib
matplotlib.use('Agg')
import numpy as np
from bokeh.io import show
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.models import LogColorMapper, LinearColorMapper, HoverTool, ColumnDataSource, CheckboxGroup
from bokeh.palettes import RdYlBu10 as palette
from bokeh.plotting import figure
from COVID.extract import JHU
# from COVID import us_map
from random import random as rand
import pandas as pd
import pickle

DataSelectButtons = CheckboxGroup(labels=["Cases of Coronavirus", "Restaurant Dining", "Employment rates"], active=[0])

[stateBorders, countyBorders] = pickle.load(open("./COVID/extract/regionBorders.p", "rb"))

statesDF = JHU.getStateDF()
state_regionalDF = JHU.getState_RegionalDF()
countriesDF = JHU.getCountriesDF()
countyDF = JHU.getCountiesDF()

palette = tuple(palette)

state_xs = [stateBorders[state]["lons"] for state in stateBorders if state]
state_ys = [stateBorders[state]["lats"] for state in stateBorders if state]

state_names = [stateBorders[state]["name"] for state in stateBorders]
# state_names = [county['state'] for county in counties.values()]

state_val = []
for state in stateBorders:
    if (state in statesDF.columns):
        state_val.append(np.max(statesDF[state].confirmed))
    else:
        print(state + ' does not have any records of cases')
        state_val.append(0)

# color_mapper = LinearColorMapper(palette=palette)

usData = ColumnDataSource(data = dict(
    x=state_xs,
    y=state_ys,
    val=state_val,
    state=state_names))

gData = ColumnDataSource(data=dict(
    date=countriesDF['US'].time.astype(str),
    time=countriesDF['US'].time,
    confirmed=countriesDF['US'].confirmed,
    recovered=countriesDF['US'].recovered,
    deaths=countriesDF['US'].deaths))

TOOLS = "pan,wheel_zoom, tap, reset,hover,save"
TOOLS2 = "pan,wheel_zoom,reset,save"

graphPlot = figure(tools=TOOLS2, x_axis_type='datetime', tooltips=[
               ("Date", "@date"), ("confirmed", "@confirmed"), ('recovered', '@recovered'), ('died', '@deaths')
           ], width=300, height=300)
graphPlot.line('time', 'confirmed', source=gData, line_color='black')
graphPlot.line('time', 'recovered', source=gData, line_color='green')
graphPlot.line('time', 'deaths', source=gData, line_color='red')
graphPlot.yaxis.axis_label = '# of people'
graphPlot.xaxis.axis_label = 'Date'

stateData = ColumnDataSource(data={'x': [], 'y': [], 'name': [], 'val': [], 'state': []})

color_mapper = LinearColorMapper(palette=palette)
color_mapper2 = LogColorMapper(palette=palette)

statePlot = figure(title="Coronavirus map", tools=TOOLS,
                x_axis_location=None, y_axis_location=None,
                tooltips=[('name','@name'),("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('State', '@state')],
                   height=300)

statePlot.grid.grid_line_color = None
statePlot.hover.point_policy = "follow_mouse"
statePlot.patches('x', 'y', source=stateData,
               fill_color={'field': 'val', 'transform': color_mapper},
               fill_alpha=0.7, line_color="white", line_width=0.5)

state = 'CA'
stateCountyDF = pd.DataFrame()

def updateState():
    global stateCountyDF, state
    print(state)
    stateCountyDF = state_regionalDF[state_regionalDF['state'] == state]
    stateCountyBorders = countyBorders[countyBorders['state'] == state]
    county_xs = [stateCountyBorders.iloc[i, :]['lons'] for i in range(len(stateCountyBorders))]
    county_ys = [stateCountyBorders.iloc[i, :]['lats'] for i in range(len(stateCountyBorders))]
    county_names = [stateCountyBorders.iloc[i, :]['county_name'] for i in range(len(stateCountyBorders))]
    state_names = [state for i in range(len(stateCountyBorders))]
    # county_val = [rand() for i in range(len(stateCounties))]
    county_val = []
    for county in county_names:
        if county in list(stateCountyDF['county_name']):
            confirmed_t = stateCountyDF[stateCountyDF['county_name'] == county].confirmed.values[0]
            if np.isnan(confirmed_t[-1]):
                lastIdx = len(confirmed_t) - 2
            else:
                lastIdx = len(confirmed_t) - 1
            county_val.append(np.max(confirmed_t[:lastIdx]))
            # print(np.max(confirmed_t[:lastIdx]))
        else:
            county_val.append(0)

    stateData.data = dict(
        x=county_xs,
        y=county_ys,
        name=county_names,
        val=county_val,
        state=state_names)

    lenTime = np.min([len(statesDF[state].time), len(statesDF[state].confirmed), len(statesDF[state].recovered), len(statesDF[state].deaths)])
    gData.data = dict(date=statesDF[state].time.astype(str)[0:lenTime],
        time=statesDF[state].time[0:lenTime],
        confirmed=statesDF[state].confirmed[0:lenTime],
        recovered=statesDF[state].recovered[0:lenTime],
        deaths=statesDF[state].deaths[0:lenTime])

    # statePlot.x_range.start = -125
    # statePlot.x_range.end = -65
    # statePlot.y_range.start = 23
    # statePlot.y_range.end = 50

    graphPlot.title.text = stateBorders[state]['name']
    statePlot.title.text = stateBorders[state]['name']
    return

updateState()

usPlot = figure(title="Cases of Coronavirus", tools=TOOLS,
                x_axis_location=None, y_axis_location=None,
                tooltips=[("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('State', '@state')],
                width=60 * 15, height=27 * 15)
usPlot.grid.grid_line_color = None
usPlot.x_range.start = -125
usPlot.x_range.end = -65
usPlot.y_range.start = 23
usPlot.y_range.end = 50
usPlot.hover.point_policy = "follow_mouse"

usPlot.patches('x', 'y', source=usData,
               fill_color={'field': 'val', 'transform': color_mapper},
               fill_alpha=0.7, line_color="white", line_width=0.5)

def us_tap_handler(attr, old, new):
    global state
    # index = new[0]
    # print(attr)
    # print([x for x in list(locals().keys()) if x[0] != '_'])
    if len(new) == 0:
        print('US')
        graphPlot.title.text = 'US'
        gData.data = dict(
            date=countriesDF['US'].time.astype(str),
            time=countriesDF['US'].time,
            confirmed=countriesDF['US'].confirmed,
            recovered=countriesDF['US'].recovered,
            deaths=countriesDF['US'].deaths)
    else:
        state = stateBorders.columns[new[0]]
        print(state)
        updateState()
    return

def state_tap(attr, old, new):
    global state, stateCountyDF, statesDF, stateBorders
    print(state)
    stateCountyDF = state_regionalDF[state_regionalDF['state'] == state]
    print(new)
    if len(new) == 0:
        graphPlot.title.text = stateBorders[state]['name']
        lenTime = np.min([len(statesDF[state].time), len(statesDF[state].confirmed), len(statesDF[state].recovered),
                          len(statesDF[state].deaths)])
        gData.data = dict(
            date=statesDF[state].time.astype(str)[0:lenTime],
            time=statesDF[state].time[0:lenTime],
            confirmed=statesDF[state].confirmed[0:lenTime],
            recovered=statesDF[state].recovered[0:lenTime],
            deaths=statesDF[state].deaths[0:lenTime])
    else:
        stateCountyDF = state_regionalDF[state_regionalDF['state'] == state]
        stateCountyBorders = countyBorders[countyBorders['state'] == state]
        county = stateCountyBorders.county_name.iloc[new[0]]
        print(stateBorders[state]['name'])
        print(county)
        if len(stateCountyDF[stateCountyDF['county_name'] == county].time.values)==0:
            return
        date_t= stateCountyDF[stateCountyDF['county_name'] == county].time.values[0].astype(str)
        time_t= stateCountyDF[stateCountyDF['county_name'] == county].time.values[0]
        confirmed_t= stateCountyDF[stateCountyDF['county_name'] == county].confirmed.values[0]
        recovered_t = stateCountyDF[stateCountyDF['county_name'] == county].recovered.values[0]
        deaths_t = stateCountyDF[stateCountyDF['county_name'] == county].deaths.values[0]
        lenTime = np.min([len(time_t), len(confirmed_t),len(recovered_t), len(deaths_t)])
        gData.data = dict(
            date=date_t[0:lenTime],
            time=time_t[0:lenTime],
            confirmed=confirmed_t[0:lenTime],
            recovered=recovered_t[0:lenTime],
            deaths=deaths_t[0:lenTime])
        graphPlot.title.text = county

        # state = stateBorders.columns[new[0]]
        # print(state)
        # statePlot.title.text = stateBorders[state]['name']
        # updateState(state=state)
    return

usData.selected.on_change("indices", us_tap_handler)
stateData.selected.on_change("indices", state_tap)


layout = column(row(usPlot, DataSelectButtons), row(graphPlot, statePlot))
# show(layout)

#
doc = curdoc()
doc.title = "Coronavirus Forecaster"
doc.add_root(layout)
# # Run this in the command line:

# bokeh serve --show --log-level=debug US_coronavirus_map.py