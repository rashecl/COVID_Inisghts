from bokeh.io import show
from bokeh.models import LogColorMapper, LinearColorMapper
from bokeh.palettes import RdYlBu6 as palette
from bokeh.plotting import figure
from bokeh.sampledata.us_states import data as states
from COVID.extract import JHU
import numpy as np
import pandas as pd
states = pd.DataFrame(states) # This contains boundaries for each state
states['D.C.'] = states.pop('DC')
statesDF = JHU.getStateDF()

palette = tuple(palette)
#
# counties = {
#     code: county for code, county in counties.items() if (county["state"] not in ['ak', 'hi', 'pr', 'as', 'gu', 'mp', 'vi'])
# }

excludeStates = ['AK', 'HI', 'PR', 'VI']
state_xs = [states[state]["lons"] for state in states if state if state not in excludeStates]
state_ys = [states[state]["lats"] for state in states if state if state not in excludeStates]

state_names = [states[state]["name"] for state in states if state not in excludeStates]
# state_names = [county['state'] for county in counties.values()]

state_val = []
for state in states:
    print(state)
    if (state in statesDF.columns) and (state not in excludeStates):
        state_val.append(statesDF[state].confirmed[-1])
    elif (state not in excludeStates):
        print(state)
        state_val.append(0)

color_mapper = LinearColorMapper(palette=palette)

data=dict(
    x=state_xs,
    y=state_ys,
    name=state_names,
    val=state_val,
    state=state_names
)

TOOLS = "pan,wheel_zoom, reset,hover,save"

p = figure(title="Coronavirus map", tools=TOOLS,
    x_axis_location=None, y_axis_location=None,
    tooltips=[
        ("Name", "@name"), ("value", "@val"), ("(Long, Lat)", "($x, $y)"), ('state', '@state')
    ], width=60*15, height=27*15)
p.grid.grid_line_color = None
p.x_range.start = -125
p.x_range.end = -65
p.y_range.start = 23
p.y_range.end = 50
p.hover.point_policy = "follow_mouse"

p.patches('x', 'y', source=data,
          fill_color={'field': 'val', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

show(p)