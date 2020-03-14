from bokeh.io import show
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.models import LogColorMapper, LinearColorMapper, HoverTool
from bokeh.palettes import RdYlBu11 as palette
from bokeh.plotting import figure
from bokeh.sampledata.us_states import data as states
from bokeh.sampledata.us_counties import data as counties
from COVID.extract import JHU
from random import random as rand
import numpy as np
import pandas as pd

states = pd.DataFrame(states)  # This contains boundaries for each state
states['D.C.'] = states.pop('DC')
statesDF = JHU.getStateDF()
countries = JHU.getCountryDF()

palette = tuple(palette)

excludeStates = ['AK', 'HI', 'PR', 'VI']
state_xs = [states[state]["lons"] for state in states if state if state not in excludeStates]
state_ys = [states[state]["lats"] for state in states if state if state not in excludeStates]

state_names = [states[state]["name"] for state in states if state not in excludeStates]
# state_names = [county['state'] for county in counties.values()]

state_val = []
for state in states:
    if (state in statesDF.columns) and (state not in excludeStates):
        state_val.append(statesDF[state].confirmed[-1])
    elif state not in excludeStates:
        print(state + ' does not have any cases')
        state_val.append(0)

color_mapper = LinearColorMapper(palette=palette)

usData = dict(
    x=state_xs,
    y=state_ys,
    val=state_val,
    state=state_names)

gData = dict(
    date=countries['US'].time.astype(str),
    time=countries['US'].time,
    confirmed=countries['US'].confirmed,
    recovered=countries['US'].recovered,
    deaths=countries['US'].deaths)

state_counties = {
    code: county for code, county in counties.items() if county["state"] == 'ca'}

county_xs = [county["lons"] for county in state_counties.values()]
county_ys = [county["lats"] for county in state_counties.values()]

county_names = [county['name'] for county in state_counties.values()]
state_names = [county['state'] for county in state_counties.values()]

county_val = [rand() for county_id in state_counties]
color_mapper = LinearColorMapper(palette=palette)

stateData=dict(
    x=county_xs,
    y=county_ys,
    name=county_names,
    val=county_val,
    state=state_names
)


TOOLS = "pan,wheel_zoom, reset,hover,save"

usPlot = figure(title="Coronavirus map", tools=TOOLS,
                x_axis_location=None, y_axis_location=None,
                tooltips=[("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('State', '@state')
           ], width=60 * 15, height=27 * 15)
usPlot.grid.grid_line_color = None
usPlot.x_range.start = -125
usPlot.x_range.end = -65
usPlot.y_range.start = 23
usPlot.y_range.end = 50
usPlot.hover.point_policy = "follow_mouse"

TOOLS2 = "pan,wheel_zoom,reset,save"
graphPlot = figure(tools=TOOLS2, x_axis_type='datetime', tooltips=[
               ("Date", "@date"), ("confirmed", "@confirmed"), ('recovered', '@recovered'), ('died', '@deaths')
           ], width=300, height=300)
graphPlot.line('time', 'confirmed', source=gData, line_color='black')
graphPlot.line('time', 'recovered', source=gData, line_color='green')
graphPlot.line('time', 'deaths', source=gData, line_color ='red')
graphPlot.yaxis.axis_label = '# of people'
graphPlot.xaxis.axis_label = 'Date'

usPlot.patches('x', 'y', source=usData,
               fill_color={'field': 'val', 'transform': color_mapper},
               fill_alpha=0.7, line_color="white", line_width=0.5)

statePlot = figure(title="Coronavirus map", tools=TOOLS,
                x_axis_location=None, y_axis_location=None,
                tooltips=[('name','@name'),("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('State', '@state')
           ], height=300)
color_mapper2 = LogColorMapper(palette=palette)
statePlot.grid.grid_line_color = None
# statePlot.x_range.start = -125
# statePlot.x_range.end = -65
# statePlot.y_range.start = 23
# statePlot.y_range.end = 50
statePlot.hover.point_policy = "follow_mouse"
statePlot.patches('x', 'y', source=stateData,
               fill_color={'field': 'val', 'transform': color_mapper2},
               fill_alpha=0.7, line_color="white", line_width=0.5)

layout = column(usPlot, row(graphPlot, statePlot))
doc = curdoc()
doc.title = "Coronavirus Forecaster"
# doc.add_root(layout)

show(layout)
