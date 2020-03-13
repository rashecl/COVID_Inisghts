from bokeh.io import show
from bokeh.models import LogColorMapper
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure
from random import random as rand
from bokeh.sampledata.unemployment import data as unemployment
from bokeh.sampledata.us_counties import data as counties

palette = tuple(reversed(palette))

counties = {
    code: county for code, county in counties.items() if (county["state"] not in ['ak', 'hi', 'pr', 'as', 'gu', 'mp', 'vi'])
}

county_xs = [county["lons"] for county in counties.values()]
county_ys = [county["lats"] for county in counties.values()]

county_names = [county['name'] for county in counties.values()]
state_names = [county['state'] for county in counties.values()]

county_val = [rand() for county_id in counties]
color_mapper = LogColorMapper(palette=palette)

data=dict(
    x=county_xs,
    y=county_ys,
    name=county_names,
    val=county_val,
    state=state_names
)

TOOLS = "pan,wheel_zoom,reset,hover,save"

p = figure(
    title="Infection rates, 2020", tools=TOOLS,
    x_axis_location=None, y_axis_location=None,
    tooltips=[
        ("Name", "@name"), ("Value", "@val%"), ("(Long, Lat)", "($x, $y)"), ('state', '@state')
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