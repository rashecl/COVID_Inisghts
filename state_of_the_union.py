import matplotlib

matplotlib.use('Agg')
import numpy as np
from bokeh.io import show
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.models import LogColorMapper, LinearColorMapper, ColorBar, ColumnDataSource, LogTicker, Select, Div
from bokeh.models import WheelZoomTool, TapTool, SaveTool, ResetTool, PanTool, HoverTool, Range1d, BoxZoomTool, \
    FuncTickFormatter
from bokeh.models import TickFormatter
from bokeh.palettes import RdYlBu10 as palette, all_palettes
from bokeh.plotting import figure
import pandas as pd
import pickle

cities = pd.read_csv('./COVID/uscities.csv', usecols=[0, 1, 5, 6, 7])
[stateBorders, countyBorders] = pickle.load(open("./COVID/regionBorders.p", "rb"))
[usPopulation, statePopulations, countyPopulations, cityPopulations] = pickle.load(
    open("./COVID/regionPopulations.p", "rb"))

[countyDF, stateDF_NYT, stateDF_CT, usDF_NYT, usDF_CT, lastUpdated] = pickle.load(
    open("./COVID/CovidCounts.p", "rb"))
print(lastUpdated)

# palette = tuple(palette)
palette = tuple([all_palettes['Turbo'][256][idx] for idx in range(50, 256)])
# color_mapper = LinearColorMapper(palette=palette)
color_mapper = LogColorMapper(palette=palette, low=1, high=200000)

us_TOOLS = [PanTool(), BoxZoomTool(), WheelZoomTool(), TapTool(), ResetTool()]
state_TOOLS = [PanTool(), BoxZoomTool(), WheelZoomTool(), TapTool(), ResetTool()]
cumul_TOOLS = [BoxZoomTool(), PanTool(), WheelZoomTool(), ResetTool(), SaveTool()]
daily_TOOLS = [BoxZoomTool(), PanTool(), WheelZoomTool(), ResetTool(), SaveTool()]
cumulCritical_TOOLS = [BoxZoomTool(), PanTool(), WheelZoomTool(), ResetTool(), SaveTool()]
dailyCritical_TOOLS = [BoxZoomTool(), PanTool(), WheelZoomTool(), ResetTool(), SaveTool()]
dailyDeath_TOOLS = [BoxZoomTool(), PanTool(), WheelZoomTool(), ResetTool(), SaveTool()]
colorBySelector = Select(title="Color by:", value="cases",
                         options=[("cases", "Cases"), ("deaths", "Deaths"),
                                  ("caseRate", "Cases/100k"), ("deathRate", "Deaths/100k"),
                                  ("testingRate", "Tests/100k")])
# options=["cases", "deaths", "caseRate", "deathRate", "testingRate"])
old_colorBy = 'cases'
new_colorBy = 'cases'
# A) Define data and plot structures

# 1) Map of US
usData = ColumnDataSource(
    data=dict(x=[], y=[], cases=[], state=[], deaths=[], caseRate=[], deathRate=[], testingRate=[], colorBy=[]))
usPlot = figure(title="Coronavirus Map: " + new_colorBy, tools=us_TOOLS,
                x_axis_location=None, y_axis_location=None,
                width=60 * 15, height=27 * 15)
usPlot.grid.grid_line_color = None
usPlot.x_range = Range1d(-125, -65, bounds=(-145, -45))
usPlot.y_range = Range1d(23, 50, bounds=(13, 60))
# usPlot.image_url(url=['https://www.your-vector-maps.com/_kepek/_grey_images/USA-mercator-vector-map.jpg'], x=-126.5, y=51.2, w=61, h=30)
statePatches = usPlot.patches('x', 'y', source=usData,
                              fill_color={'field': 'colorBy', 'transform': color_mapper},
                              fill_alpha=0.7, line_color="white", line_width=0.5)
cityData = ColumnDataSource(data=dict(lat=cities['lat'], lon=cities['lon'],
                                      population=cities['population'],
                                      city=cities['city'],
                                      state=cities['state'],
                                      markerSize=cities['population'].apply(lambda x: x ** (1 / 3) / 30)))

cityPoints = usPlot.circle('lon', 'lat', size='markerSize', color="gray", fill_alpha=0.7, source=cityData)
usPlot.add_tools(
    HoverTool(renderers=[statePatches], tooltips=[('State', '@state'),
                                                  ("Cases", "@cases{(0.00 a)}"),
                                                  ("Deaths", "@deaths{(0,00)}"),
                                                  ("Cases/100k", "@caseRate{(0,0)}"),
                                                  ("Deaths/100k", "@deathRate{(0.0)}"),
                                                  ("Tests/100k", "@testingRate{(0,0)}")])
)

usPlot.add_tools(
    HoverTool(renderers=[cityPoints], tooltips=[("city", "@city"), ("State", "@state"),
                                                ("Population", "@population{(0,0)}")])
)
# usPlot.hover.point_policy = "follow_mouse"
usPlot.toolbar.active_drag = us_TOOLS[0]
usPlot.toolbar.active_scroll = us_TOOLS[2]

tick_labels = {'0': '0', '1': '1', '10': '10',
               '100': '100', '1000': '1000',
               '10000': '10,000', '100000': '100,000', '1,000,000': '1,000,000'}

us_color_bar = ColorBar(color_mapper=color_mapper, ticker=LogTicker(),
                        label_standoff=12, border_line_color=None, orientation='horizontal', location=(0, 0),
                        major_label_overrides=tick_labels)
usPlot.add_layout(us_color_bar, 'below')
# usColorBar.right[0].formatter.use_scientific = False
# 2) Map of state
stateData = ColumnDataSource(data=dict(x=[], y=[], name=[], cases=[], state=[],
                                       deaths=[], caseRate=[], deathRate=[], colorBy=[]))
statePlot = figure(title="State map", tools=state_TOOLS,
                   x_axis_location=None, y_axis_location=None,
                   height=405, width=405)
statePlot.toolbar.active_drag = state_TOOLS[0]
statePlot.toolbar.active_scroll = state_TOOLS[2]
statePlot.grid.grid_line_color = None
# statePlot.hover.point_policy = "follow_mouse"
countyPatches = statePlot.patches('x', 'y', source=stateData,
                                  fill_color={'field': 'colorBy', 'transform': color_mapper},
                                  fill_alpha=0.7, line_color="white", line_width=0.5)

stateCityData = ColumnDataSource(data=dict(lat=[], lon=[],
                                           population=[], city=[],
                                           state=[], markerSize=[]))

stateCityPoints = statePlot.circle('lon', 'lat', size='markerSize', color="gray", fill_alpha=0.7, source=stateCityData)

statePlot.add_tools(HoverTool(renderers=[countyPatches], tooltips=[('Name', '@name'), ("Cases", "@cases{(0,00)}"),
                                                                   ("Deaths", "@deaths{(0,00)}"),
                                                                   ("Cases/100k", "@caseRate{(0,0)}"),
                                                                   ("Deaths/100k", "@deathRate{(0.0)}"),
                                                                   ('State', '@state')]))

statePlot.add_tools(HoverTool(renderers=[stateCityPoints], tooltips=[("city", "@city"), ("State", "@state"),
                                                                     ("Population", "@population{(0,0)}")]))
# 3,4) Cumulative temporal graphs (tests, positive):

cumulativeData_CT = ColumnDataSource(data=dict(time=[], total_positive=[], total_testResults=[],
                                               total_hospitalized=[], total_ICU=[], total_deaths=[], source=[],
                                               testingRate=[]))
cumulativeData_NYT = ColumnDataSource(data=dict(time=[], total_positive=[], total_deaths=[], source=[]))
cumulPlot = figure(tools=cumul_TOOLS, x_axis_type='datetime', width=650, height=250)
cumulPlot.left[0].formatter.use_scientific = False
total_positive_CT = cumulPlot.line('time', 'total_positive', source=cumulativeData_CT, line_color='blue', line_width=2,
                                   legend_label='positive_CT')
total_positive_NYT = cumulPlot.line('time', 'total_positive', source=cumulativeData_NYT, line_color='lightblue',
                                    line_width=2,
                                    legend_label='positive_NYT')
total_testResults = cumulPlot.line('time', 'total_testResults', source=cumulativeData_CT, line_color='green',
                                   line_width=2,
                                   legend_label='total_testResults')
# total_positive_NYT.visible = False
cumulPlot.yaxis.axis_label = '# of people'
# cumulPlot.yaxis.formatter = FuncTickFormatter(code="""
#     parts = tick.toString().split(".");
#     parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
#     return parts.join(".");
#     """)
cumulPlot.xaxis.axis_label = 'Date'
cumulPlot.legend.location = "top_left"
cumulPlot.legend.click_policy = "hide"
cumulPlot.add_tools(
    HoverTool(renderers=[total_positive_CT],
              tooltips=[("total_positive", "@total_positive{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
cumulPlot.add_tools(
    HoverTool(renderers=[total_positive_NYT],
              tooltips=[("total_positive", "@total_positive{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
cumulPlot.add_tools(
    HoverTool(renderers=[total_testResults],
              tooltips=[("total_testResults", "@total_testResults{(0,00)}"),
                        ("Tests/100k", "@testingRate{(0.0)}"),
                        ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
# 4) Cumulative critical cases (deaths for now):

cumulCriticalPlot = figure(tools=cumulCritical_TOOLS, x_axis_type='datetime', width=650, height=250,
                           x_range=cumulPlot.x_range)
cumulCriticalPlot.left[0].formatter.use_scientific = False
total_deaths_CT = cumulCriticalPlot.line('time', 'total_deaths', source=cumulativeData_CT, line_color='red',
                                         line_width=2,
                                         legend_label='totalDeaths_CT')
total_deaths_NYT = cumulCriticalPlot.line('time', 'total_deaths', source=cumulativeData_NYT, line_color='magenta',
                                          line_width=2, legend_label='totalDeaths_NYT')
# total_deaths_NYT.visible = False
cumulCriticalPlot.yaxis.axis_label = '# of people'
# cumulCriticalPlot.yaxis.formatter= FuncTickFormatter(code="""
#     parts = tick.toString().split(".");
#     parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
#     return parts.join(".");
#     """)
cumulCriticalPlot.xaxis.axis_label = 'Date'
cumulCriticalPlot.legend.location = "top_left"
cumulCriticalPlot.legend.click_policy = "hide"
cumulCriticalPlot.add_tools(
    HoverTool(renderers=[total_deaths_CT], tooltips=[("total_deaths", "@total_deaths{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
cumulCriticalPlot.add_tools(
    HoverTool(renderers=[total_deaths_NYT], tooltips=[("total_deaths", "@total_deaths{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
# 5-7) Daily temporal graphs:

dailyData_CT = ColumnDataSource(data=dict(time=[], new_positive=[], new_testResults=[],
                                          current_hospitalized=[], current_ICU=[], new_deaths=[], source=[], states_reporting_hosp=[], states_reporting_ICU=[]))
dailyData_NYT = ColumnDataSource(data=dict(time=[], new_positive=[], new_deaths=[], source=[]))

dailyPlot = figure(tools=daily_TOOLS, x_axis_type='datetime', width=650, height=250, title="Daily statistics",
                   x_range=cumulPlot.x_range)
dailyPlot.left[0].formatter.use_scientific = False

new_positive_CT = dailyPlot.line('time', 'new_positive', source=dailyData_CT, line_color='blue', line_width=2,
                                 legend_label='new_positive_CT')
new_testResults = dailyPlot.line('time', 'new_testResults', source=dailyData_CT, line_color='green', line_width=2,
                                 legend_label='new_testResults')
new_positive_NYT = dailyPlot.line('time', 'new_positive', source=dailyData_NYT, line_color='lightblue', line_width=2,
                                  legend_label='new_positive_NYT')
# new_positive_NYT.visible = False
dailyPlot.add_tools(
    HoverTool(renderers=[new_positive_CT], tooltips=[("new_positive", "@new_positive{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
dailyPlot.add_tools(
    HoverTool(renderers=[new_testResults],
              tooltips=[("new_testResults", "@new_testResults{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
dailyPlot.add_tools(
    HoverTool(renderers=[new_positive_NYT], tooltips=[("new_positive", "@new_positive{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)

dailyPlot.toolbar.active_drag = None  # daily_TOOLS[1]
dailyPlot.yaxis.axis_label = '# of people'
# dailyPlot.yaxis.formatter = formatter = FuncTickFormatter(code="""
#     parts = tick.toString().split(".");
#     parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
#     return parts.join(".");
#     """)
dailyPlot.xaxis.axis_label = 'Date'
dailyPlot.legend.location = "top_left"
dailyPlot.legend.click_policy = "hide"

# 7 Daily death graph:
dailyDeathPlot = figure(tools=dailyCritical_TOOLS, x_axis_type='datetime', width=650, height=250,
                        title="Daily death statistics", x_range=cumulPlot.x_range)
dailyDeathPlot.left[0].formatter.use_scientific = False

new_deaths_CT = dailyDeathPlot.line('time', 'new_deaths', source=dailyData_CT, line_color='black', line_width=2,
                                    legend_label='new_deaths_CT')
new_deaths_NYT = dailyDeathPlot.line('time', 'new_deaths', source=dailyData_NYT, line_color='grey', line_width=2,
                                     legend_label='new_deaths_NYT')
# new_deaths_NYT.visible = False
dailyDeathPlot.add_tools(
    HoverTool(renderers=[new_deaths_CT], tooltips=[("new_deaths", "@new_deaths{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)
dailyDeathPlot.add_tools(
    HoverTool(renderers=[new_deaths_NYT], tooltips=[("new_deaths", "@new_deaths{(0,00)}"), ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)

dailyDeathPlot.toolbar.active_drag = None  # dailyDeath_TOOLS[1]
dailyDeathPlot.yaxis.axis_label = '# of people'
# dailyDeathPlot.yaxis.formatter = FuncTickFormatter(code="""
#     parts = tick.toString().split(".");
#     parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
#     return parts.join(".");
#     """)
dailyDeathPlot.xaxis.axis_label = 'Date'
dailyDeathPlot.legend.location = "top_left"
dailyDeathPlot.legend.click_policy = "hide"

# 7) dailyCritical plot:

dailyCriticalPlot = figure(tools=dailyCritical_TOOLS, x_axis_type='datetime', width=650, height=250,
                           title="*Daily hospitalization statistics", x_range=cumulPlot.x_range)
dailyCriticalPlot.left[0].formatter.use_scientific = False

current_hospitalized = dailyCriticalPlot.line('time', 'current_hospitalized', source=dailyData_CT, line_color='orange',
                                              line_width=2, legend_label='current_hospitalized')
current_ICU = dailyCriticalPlot.line('time', 'current_ICU', source=dailyData_CT, line_color='red', line_width=2,
                                     legend_label='current_ICU')
# new_deaths_NYT.visible = False
dailyCriticalPlot.add_tools(HoverTool(renderers=[current_hospitalized],
                                      tooltips=[("current_hospitalized", "@current_hospitalized{(0,00)}"),
                                                ("states_reporting_hosp", "@states_reporting_hosp"),
                                                ("date", "@time{%F}")],
                                      formatters={'@time': 'datetime'})
                            )
dailyCriticalPlot.add_tools(
    HoverTool(renderers=[current_ICU], tooltips=[("current_ICU", "@current_ICU{(0,00)}"),
                                                 ("states_reporting_ICU", "@states_reporting_ICU"),
                                                 ("date", "@time{%F}")],
              formatters={'@time': 'datetime'})
)

dailyCriticalPlot.toolbar.active_drag = None  # dailyCritical_TOOLS[1]
dailyCriticalPlot.yaxis.axis_label = '# of people'
# dailyCriticalPlot.yaxis.formatter = FuncTickFormatter(code="""
#     parts = tick.toString().split(".");
#     parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
#     return parts.join(".");
#     """)
dailyCriticalPlot.xaxis.axis_label = 'Date'
dailyCriticalPlot.legend.location = "top_left"
dailyCriticalPlot.legend.click_policy = "hide"

print("Completed defining plot structures")

# B) Define the actual data for the plots:
# 1) Define data for US map plot:
state_xs = [stateBorders[state]["lons"] for state in stateBorders if state]
state_ys = [stateBorders[state]["lats"] for state in stateBorders if state]
state_names = [stateBorders[state]["name"] for state in stateBorders]

caseRate = []
deathRate = []
testingRate = []
deaths = []
cases = []
for state in stateBorders:
    if (state in list(stateDF_CT.state.unique())):
        cases.append(stateDF_CT.query("state == '" + state + "'")['positive'].iloc[-1])  # latest positive
        deathRate.append(stateDF_CT.query("state == '" + state + "'")['deathRate'].iloc[-1])
        testingRate.append(stateDF_CT.query("state == '" + state + "'")['testingRate'].iloc[-1])
        deaths.append(stateDF_CT.query("state == '" + state + "'")['death'].iloc[-1])
        caseRate.append(stateDF_CT.query("state == '" + state + "'")['positiveRate'].iloc[-1])  # latest positive
    else:
        print(state + ' does not have any records of cases')
        cases.append(0)
        caseRate.append(0)
        deathRate.append(0)
        testingRate.append(0)
        deaths.append(0)
usColorBys = dict(x=state_xs, y=state_ys, cases=cases, state=state_names, caseRate=caseRate,
                  deathRate=deathRate, testingRate=testingRate, deaths=deaths, colorBy=cases)
usData.data = dict(x=state_xs, y=state_ys, cases=cases, state=state_names, caseRate=caseRate,
                   deathRate=deathRate, testingRate=testingRate, deaths=deaths, colorBy=cases)
print("Completed defining data")


# 2) Define function on selection of new state:
def updateState():
    global countyDF, state, stateCountyDF, stateBorders, new_colorBy, old_colorBy, stateColorBys
    print(state)
    state_name = stateBorders[state]['name']
    stateCountyDF = countyDF.query("state == '" + state + "'")
    stateCountyBorders = countyBorders[countyBorders['state'] == state]
    county_xs = [stateCountyBorders.iloc[i, :]['lons'] for i in range(len(stateCountyBorders))]
    county_ys = [stateCountyBorders.iloc[i, :]['lats'] for i in range(len(stateCountyBorders))]
    if state != 'NY':
        county_names = [stateCountyBorders.iloc[i, :]['county'] for i in range(len(stateCountyBorders))]
    else:
        county_names = []
        for i in range(len(stateCountyBorders)):
            county_name = stateCountyBorders.iloc[i, :]['county']
            if county_name in ('Queens', 'Bronx', 'Richmond', 'Kings', 'New York'):
                county_names.append(county_name + " (NYC)")
            else:
                county_names.append(county_name)

    state_names = [state for i in range(len(stateCountyBorders))]
    # county_val = [rand() for i in range(len(stateCounties))]
    cases = []
    caseRate = []
    deaths = []
    deathRate = []

    for county in [county.split(' (NYC')[0] for county in
                   county_names]:  # TODO: Change this so it flexible handles other cities
        if (state == 'NY') and county in ('Queens', 'Bronx', 'Richmond', 'Kings', 'New York'):
            cases.append(stateCountyDF[stateCountyDF['county'] == 'New York City'].positive.values[-1])
            caseRate.append(stateCountyDF[stateCountyDF['county'] == 'New York City'].positiveRate.values[-1])
            deaths.append(stateCountyDF[stateCountyDF['county'] == 'New York City'].death.values[-1])
            deathRate.append(stateCountyDF[stateCountyDF['county'] == 'New York City'].deathRate.values[-1])

        elif county in list(stateCountyDF['county'].unique()):
            cases.append(stateCountyDF[stateCountyDF['county'] == county].positive.values[-1])
            caseRate.append(stateCountyDF[stateCountyDF['county'] == county].positiveRate.values[-1])
            deaths.append(stateCountyDF[stateCountyDF['county'] == county].death.values[-1])
            deathRate.append(stateCountyDF[stateCountyDF['county'] == county].deathRate.values[-1])

        else:
            cases.append(0)
            caseRate.append(0)
            deaths.append(0)
            deathRate.append(0)
    stateColorBys = dict(
        x=county_xs,
        y=county_ys,
        name=county_names,
        cases=cases,
        state=state_names,
        deaths=deaths,
        deathRate=deathRate,
        caseRate=caseRate)

    if new_colorBy != 'testingRate':
        stateColorBys.update({'colorBy': eval(new_colorBy)})
        statePlot.title.text = state_name + ': ' + new_colorBy
    else:
        stateColorBys.update({'colorBy': eval(old_colorBy)})
        statePlot.title.text = state_name + ': ' + old_colorBy

    stateData.data = stateColorBys

    # Set new limits and re-title state plot:
    print('Setting limits: ' + state)

    yrange = [np.nanmin(stateBorders[state]['lats']), np.nanmax(stateBorders[state]['lats'])]
    xrange = [np.nanmin(stateBorders[state]['lons']), np.nanmax(stateBorders[state]['lons'])]
    plotRange = np.diff(xrange)[0] if np.diff(xrange) > np.diff(yrange) else np.diff(yrange)[0]
    # statePlot.x_range = Range1d((xrange[0] + plotRange/2) -.55*plotRange, (xrange[0] + plotRange/2) +.55*plotRange, bounds = ((xrange[0] + plotRange/2) -.55*plotRange, (xrange[0] + plotRange/2) +.55*plotRange))
    statePlot.x_range.start = np.average(xrange) - .55 * plotRange
    statePlot.x_range.end = np.average(xrange) + .55 * plotRange
    # statePlot.y_range = Range1d((yrange[0] + plotRange/2) -.55*plotRange, (yrange[0] + plotRange/2) +.55*plotRange, bounds = ((yrange[0] + plotRange/2) -.55*plotRange, (yrange[0] + plotRange/2) +.55*plotRange))
    statePlot.y_range.start = np.average(yrange) - .55 * plotRange
    statePlot.y_range.end = np.average(yrange) + .55 * plotRange

    # state_name = stateBorders[state]['name']
    # cumulPlot.title.text = state_name + ': Cumulative testing data'
    #
    # cumulCriticalPlot.title.text = state_name + ': Cumulative deaths'
    # dailyPlot.title.text = state_name + ': Daily testing data'
    # dailyDeathPlot.title.text = state_name + ': Daily deaths'
    # dailyCriticalPlot.title.text = state_name + ': Daily hospitalization data*'
    # Update stateData:
    sourceStateData()
    return


# 3) Define data for temporal graphs:
def sourceUSdata():
    global usDF_CT, stateDF_CT
    CTdf = usDF_CT
    dailyData_CT.data = dict(
        time=CTdf['date'],
        # date=CTdf['date'].astype(str),
        new_positive=CTdf['positiveIncrease'],
        new_testResults=CTdf['totalTestResultsIncrease'],
        current_hospitalized=CTdf['hospitalizedCurrently'],
        states_reporting_hosp=stateDF_CT.groupby('date').count()['hospitalizedCurrently'],
        states_reporting_ICU=stateDF_CT.groupby('date').count()['inIcuCurrently'],
        current_ICU=CTdf['inIcuCurrently'],
        new_deaths=CTdf['deathIncrease'],
        source=CTdf['source'])

    cumulativeData_CT.data = dict(
        time=CTdf['date'],
        # date=CTdf['date'].astype(str),
        total_positive=CTdf['positive'],
        total_testResults=CTdf['totalTestResults'],
        testingRate=CTdf['testingRate'],
        total_hospitalized=CTdf['hospitalizedCumulative'],
        total_ICU=CTdf['inIcuCumulative'],
        total_deaths=CTdf['death'],
        source=CTdf['source'])

    NYTdf = usDF_NYT
    dailyData_NYT.data = dict(
        time=NYTdf['date'],
        # date=NYTdf['date'].astype(str),
        new_positive=NYTdf['positiveIncrease'],
        new_deaths=NYTdf['deathIncrease'],
        source=NYTdf['source'])

    cumulativeData_NYT.data = dict(
        time=NYTdf['date'],
        # date=NYTdf['date'].astype(str),
        total_positive=NYTdf['positive'],
        total_deaths=NYTdf['death'],
        source=NYTdf['source'])
    cumulPlot.title.text = 'United States: Cumulative testing data'
    cumulPlot.title.text = 'United States' + ': Cumulative testing data'
    cumulCriticalPlot.title.text = 'United States' + ': Cumulative deaths'
    dailyPlot.title.text = 'United States' + ': Daily testing data'
    dailyDeathPlot.title.text = 'United States' + ': Daily deaths'
    dailyCriticalPlot.title.text = 'United States' + ': Daily hospitalization data*'
    return


def sourceStateData():
    global stateCountyDF, county, state
    df = cities.query("state == '" + state + "'")
    stateCityData.data = dict(lat=df['lat'], lon=df['lon'],
                              population=df['population'],
                              city=df['city'],
                              state=df['state'],
                              markerSize=df['population'].apply(lambda x: x ** (1 / 3) / 15))

    # Update state level data:
    CTdf = stateDF_CT.query("state == '" + state + "'")
    dailyData_CT.data = dict(
        time=CTdf['date'],
        # date=CTdf['date'].astype(str),
        new_positive=CTdf['positiveIncrease'],
        new_testResults=CTdf['totalTestResultsIncrease'],
        current_hospitalized=CTdf['hospitalizedCurrently'],
        current_ICU=CTdf['inIcuCurrently'],
        new_deaths=CTdf['deathIncrease'],
        states_reporting_hosp=['N/A']*len(CTdf['hospitalizedCurrently']),
        states_reporting_ICU=['N/A'] * len(CTdf['inIcuCurrently']),
        source=CTdf['source'])

    cumulativeData_CT.data = dict(
        time=CTdf['date'],
        # date=CTdf['date'].astype(str),
        total_positive=CTdf['positive'],
        total_testResults=CTdf['totalTestResults'],
        testingRate=CTdf['testingRate'],
        total_hospitalized=CTdf['hospitalizedCumulative'],
        total_ICU=CTdf['inIcuCumulative'],
        total_deaths=CTdf['death'],
        source=CTdf['source'])

    NYTdf = stateDF_NYT.query("state == '" + state + "'")

    dailyData_NYT.data = dict(
        time=NYTdf['date'],
        # date=NYTdf['date'].astype(str),
        new_positive=NYTdf['positiveIncrease'],
        new_deaths=NYTdf['deathIncrease'],
        source=NYTdf['source'])

    cumulativeData_NYT.data = dict(
        time=NYTdf['date'],
        # date=NYTdf['date'].astype(str),
        total_positive=NYTdf['positive'],
        total_deaths=NYTdf['death'],
        source=NYTdf['source'])
    state_name = stateBorders[state]['name']
    cumulPlot.title.text = state_name + ': Cumulative testing data'

    cumulCriticalPlot.title.text = state_name + ': Cumulative deaths'
    dailyPlot.title.text = state_name + ': Daily testing data'
    dailyDeathPlot.title.text = state_name + ': Daily deaths'
    dailyCriticalPlot.title.text = state_name + ': Daily hospitalization data*'
    return


def sourceCountyData():
    global stateCountyDF, county, state
    NYTdf = stateCountyDF
    # Clear all fields first
    dailyData_CT.data = dict(
        time=[],
        new_positive=[],
        new_testResults=[],
        current_hospitalized=[],
        current_ICU=[],
        new_deaths=[],
        source=[])

    cumulativeData_CT.data = dict(
        time=[],
        total_positive=[],
        total_testResults=[],
        testingRate=[],
        total_hospitalized=[],
        total_ICU=[],
        total_deaths=[],
        source=[])

    dailyData_NYT.data = dict(
        time=NYTdf['date'],
        new_positive=NYTdf['positiveIncrease'],
        new_deaths=NYTdf['deathIncrease'],
        source=NYTdf['source'])

    cumulativeData_NYT.data = dict(
        time=NYTdf['date'],
        total_positive=NYTdf['positive'],
        total_deaths=NYTdf['death'],
        source=NYTdf['source'])

    cumulPlot.title.text = county + ': Cumulative data'
    return


# C) Define interactivity functions

def us_tap_handler(attr, old, new):
    global state
    # index = new[0]
    # print(attr)
    # print([x for x in list(locals().keys()) if x[0] != '_'])
    if len(new) == 0:
        print('US')
        sourceUSdata()
    else:
        state = stateBorders.columns[new[0]]
        print(state)
        updateState()
        stateData.selected.indices = []
    return


def state_tap(attr, old, new):
    global state, stateCountyDF, statesDF, stateBorders, county, countyDF
    print(state)
    print(new)
    if len(new) == 0:
        sourceStateData()
        pass  # updateState()
    else:
        stateCountyBorders = countyBorders[countyBorders['state'] == state]
        county = stateCountyBorders.county.iloc[new[0]]
        print(stateBorders[state]['name'])
        print(county)
        if (state == 'NY') and county in ('Queens', 'Bronx', 'Richmond', 'Kings',
                                          'New York'):  # TODO: change this code if these counties start reporting separately
            county = 'New York City'
            stateCountyDF = countyDF.query("(state == '" + state + "') & (county == 'New York City')")
        else:
            stateCountyDF = countyDF.query("(state == '" + state + "') & (county == '" + county + "')")
        if len(stateCountyDF) == 0:
            print('No data for this county: ' + county)
        else:
            pass
        sourceCountyData()

        cumulPlot.title.text = county + ': Cumulative testing data'
        cumulCriticalPlot.title.text = county + ': Cumulative deaths'
        dailyPlot.title.text = county + ': Daily testing data'
        dailyDeathPlot.title.text = county + ': Daily deaths'
        dailyCriticalPlot.title.text = county + ': Daily hospitalization data*'

        # state = stateBorders.columns[new[0]]
        # print(state)
        # statePlot.title.text = stateBorders[state]['name']
        # updateState(state=state)
    return


def colorByHandler(attr, old, new):
    global colorBy, stateColorBys, new_colorBy, old_colorBy
    old_colorBy = old
    new_colorBy = new
    print("Previous label: " + old_colorBy)
    print("Updated label: " + new_colorBy)

    usColorBys['colorBy'] = usColorBys[new_colorBy]
    usData.data = usColorBys
    usPlot.title.text = "Coronavirus Map: " + new_colorBy

    if new_colorBy != 'testingRate':
        stateColorBys['colorBy'] = stateColorBys[new_colorBy]
        stateData.data = stateColorBys
        print(stateColorBys['state'][0] + ': ' + new_colorBy)
        statePlot.title.text = stateColorBys['state'][0] + ': ' + new_colorBy
    else:
        statePlot.title.text = stateColorBys['state'][0] + ': ' + old_colorBy + " (no county level testing data)"
    return


usData.selected.on_change("indices", us_tap_handler)
stateData.selected.on_change("indices", state_tap)
colorBySelector.on_change("value", colorByHandler)
layout = column(row(usPlot, column(statePlot, colorBySelector)),
                row(cumulPlot, dailyPlot),
                row(cumulCriticalPlot, dailyDeathPlot),
                row(Div(
                    text='*Hospitalization statistics may be confounded by the # of states reporting. ' + '<br> <b>Last updated:</b> ' + str(
                        lastUpdated)[0:16] + '<br> <b>Sources:</b> New York Times (NYT) and The COVID Tracking Project (CT)', width=300,
                    style={'font-size': '150%', 'color': 'black'}),
                    dailyCriticalPlot))
# Initiate with US data:
sourceUSdata()
# show(layout)
doc = curdoc()
doc.title = "US Coronavirus Map"
doc.add_root(layout)
# # Run this in the command line:

# bokeh serve --show --log-level=debug state_of_the_union.py
