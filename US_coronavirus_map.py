import matplotlib
matplotlib.use('Agg')
import numpy as np
from bokeh.io import show
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.models import LogColorMapper, LinearColorMapper, HoverTool, ColumnDataSource, CheckboxGroup
from bokeh.models import WheelZoomTool, TapTool, SaveTool, ResetTool, PanTool, HoverTool, Range1d
from bokeh.palettes import RdYlBu10 as palette, all_palettes
from bokeh.plotting import figure
from COVID.extract import JHU
# from COVID import us_map
import pandas as pd
import pickle


DataSelectButtons = CheckboxGroup(labels=["Cases of coronavirus", "More to come...", "Like testing...", "and other suggestions..."], active=[0])

[stateBorders, countyBorders] = pickle.load(open("./COVID/extract/regionBorders.p", "rb"))

countriesDF = JHU.getCountriesDF()
statesDF = JHU.getStateDF()
state_regionalDF = JHU.getState_RegionalDF()
countyDF = JHU.getCountiesDF()

# palette = tuple(palette)
palette = tuple([all_palettes['Turbo'][256][idx] for idx in range(50,256)])
color_mapper = LinearColorMapper(palette=palette)

# palette = tuple(all_palettes['Turbo'][256])

TOOLS1 = [PanTool(), WheelZoomTool(), TapTool(), HoverTool(), ResetTool(), SaveTool()]
TOOLS2 = [PanTool(), WheelZoomTool(), TapTool(), HoverTool(), ResetTool(), SaveTool()]
TOOLS3 = [PanTool(), WheelZoomTool(), HoverTool(), ResetTool(), SaveTool()]
""" Define data and plot structures for the following plots:
1) Map of US
2) Map of state
3) Graph showing temporal trends
"""
# 1) Map of US
usData = ColumnDataSource(data=dict(x=[], y=[], val=[], state=[]))
usPlot = figure(title="Cases of Coronavirus", tools=TOOLS1,
                x_axis_location=None, y_axis_location=None,
                tooltips=[("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('State', '@state')],
                width=60 * 15, height=27 * 15)
usPlot.grid.grid_line_color = None
usPlot.x_range = Range1d(-125, -65, bounds=(-150, -30))
usPlot.y_range = Range1d(23, 50, bounds = (15, 75))
usPlot.hover.point_policy = "follow_mouse"
usPlot.patches('x', 'y', source=usData,
               fill_color={'field': 'val', 'transform': color_mapper},
               fill_alpha=0.7, line_color="white", line_width=0.5)
usPlot.toolbar.active_scroll=TOOLS1[1]

# 2) Map of state
stateData = ColumnDataSource(data={'x': [], 'y': [], 'name': [], 'val': [], 'state': []})
statePlot = figure(title="Coronavirus map", tools=TOOLS2,
                x_axis_location=None, y_axis_location=None,
                tooltips=[('name','@name'),("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('State', '@state')],
                   height=400, width=400)
statePlot.toolbar.active_scroll=TOOLS2[1]
statePlot.grid.grid_line_color = None
statePlot.hover.point_policy = "follow_mouse"
statePlot.patches('x', 'y', source=stateData,
               fill_color={'field': 'val', 'transform': color_mapper},
               fill_alpha=0.7, line_color="white", line_width=0.5)

# 3) Graph of temporal variables
gData = ColumnDataSource(data=dict(date=[], time=[], confirmed=[], recovered=[], deaths=[]))
graphPlot = figure(tools=TOOLS3, x_axis_type='datetime', tooltips=[
               ("Date", "@date"), ("confirmed", "@confirmed"), ('recovered', '@recovered'), ('died', '@deaths')
           ], width=500, height=400)
graphPlot.line('time', 'confirmed', source=gData, line_color='black')
graphPlot.line('time', 'recovered', source=gData, line_color='green')
graphPlot.line('time', 'deaths', source=gData, line_color='red')
graphPlot.yaxis.axis_label = '# of people'
graphPlot.xaxis.axis_label = 'Date'

""" Not it's time to define the actual data"""
# 1) Define actual data for US map:
state_xs = [stateBorders[state]["lons"] for state in stateBorders if state]
state_ys = [stateBorders[state]["lats"] for state in stateBorders if state]
state_names = [stateBorders[state]["name"] for state in stateBorders]
state_val = []
for state in stateBorders:
    if (state in statesDF.columns):
        state_val.append(np.max(statesDF[state].confirmed))
    else:
        print(state + ' does not have any records of cases')
        state_val.append(0)
usData.data=dict(x=state_xs, y=state_ys, val=state_val, state=state_names)

# 2) Define data for state map
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
    yrange = [np.nanmin(stateBorders[state]['lats']), np.nanmax(stateBorders[state]['lats'])]
    xrange = [np.nanmin(stateBorders[state]['lons']), np.nanmax(stateBorders[state]['lons'])]
    plotRange = np.diff(xrange)[0] if np.diff(xrange) > np.diff(yrange) else np.diff(yrange)[0]
    # statePlot.x_range = Range1d((xrange[0] + plotRange/2) -.55*plotRange, (xrange[0] + plotRange/2) +.55*plotRange, bounds = ((xrange[0] + plotRange/2) -.55*plotRange, (xrange[0] + plotRange/2) +.55*plotRange))
    statePlot.x_range.start = np.average(xrange) -.55*plotRange
    statePlot.x_range.end = np.average(xrange) +.55*plotRange
    # statePlot.y_range = Range1d((yrange[0] + plotRange/2) -.55*plotRange, (yrange[0] + plotRange/2) +.55*plotRange, bounds = ((yrange[0] + plotRange/2) -.55*plotRange, (yrange[0] + plotRange/2) +.55*plotRange))
    statePlot.y_range.start = np.average(yrange) -.55*plotRange
    statePlot.y_range.end = np.average(yrange) +.55*plotRange

    graphPlot.title.text = stateBorders[state]['name']
    statePlot.title.text = stateBorders[state]['name']
    return
# stateCountyDF = pd.DataFrame()
state = 'CA'
updateState()

# 3) Define data for graph:
# Show US data to start
gData.data = dict(date=countriesDF['US'].time.astype(str),
    time=countriesDF['US'].time,
    confirmed=countriesDF['US'].confirmed,
    recovered=countriesDF['US'].recovered,
    deaths=countriesDF['US'].deaths)
graphPlot.title.text = 'United States'

""" Define interactivity functions"""
def us_tap_handler(attr, old, new):
    global state
    # index = new[0]
    # print(attr)
    # print([x for x in list(locals().keys()) if x[0] != '_'])
    if len(new) == 0:
        print('US')
        graphPlot.title.text = 'United States'
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
        stateData.selected.indices = []


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
doc.title = "US Coronavirus Map"
doc.add_root(layout)
# # Run this in the command line:

# bokeh serve --show --log-level=debug US_coronavirus_map.py