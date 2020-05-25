import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from pandas.io.json import json_normalize
import plotly.offline as pyo
import plotly.graph_objs as go
from dash.dependencies import Input, Output

r = requests.get('https://api.covid19api.com/world/total')
countryReq = requests.get('https://api.covid19api.com/countries')


countryDf = json_normalize(countryReq.json())

def getCountries():
    data = []
    for country,slug in zip(countryDf['Country'],countryDf['Slug']):
        data.append({'label': country,'value': slug})
    return data

def trendByCountry(df):
    trace1 = go.Bar(y=df['Date'],x=df['Cases'],name='Confirmed',orientation='h')
    data = [trace1]
    layout = go.Layout(title='Country Trend Analysis',xaxis=dict(title= 'Date'),yaxis=dict(title = 'Cases'),barmode='stack')
    return go.Figure(data=data,layout=layout)
    
#create pie chart for comparison
def createPieChart(cases,population):
    labels = ['Cases','Population']
    values = [cases, population]
    return go.Figure(data=[go.Pie(labels=labels, values=values)],layout=go.Layout(title="Cases vs Population"))


app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H2('COVID19 DATA ANALYSIS'),
    html.Div(children=[
        html.P(children="The total number of confirmed cases are {}".format(r.json()['TotalConfirmed']),className='bolder'),
        html.Label('Select Country'),
        dcc.Dropdown(
        id='country-dropdown',
        options=getCountries(),
        value='ghana'
    ),
    dcc.Graph(id='country-trend',
        animate=True
    ),
    dcc.Graph(id='pie-chart',animate=True)

    ],className='appWrapper')
],className='app')

#callbacks
@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    [Input(component_id='country-dropdown', component_property='value')]
)
def update_output_count(input_value):
    selected_country = countryDf[countryDf['Slug'] == input_value]
    #make request to world bank api to get the population of countries
    url = "http://api.worldbank.org/v2/country/{}/indicator/SP.POP.TOTL?format=json".format(selected_country['ISO2'].iloc[0])

    #remove this code in the future
    forCountry = requests.get("https://api.covid19api.com/country/{}/status/confirmed/live".format(selected_country['Slug'].iloc[0]))
    data = json_normalize(forCountry.json())
    maxCases = data['Cases'].max()

    req = requests.get(url)
    population = 0
    
    for row in req.json()[1]:
        #print(row)
        if row['value'] != None:
            population = row['value']
            break

    #print(maxCases)
    return createPieChart(maxCases,population)


@app.callback(
    Output(component_id='country-trend', component_property='figure'),
    [Input(component_id='country-dropdown', component_property='value')]
)
def update_output_div(input_value):
   # forCountry = requests.get("https://api.covid19api.com/live/country/{}".format(input_value))
    forCountry = requests.get("https://api.covid19api.com/country/{}/status/confirmed/live".format(input_value))
    data = json_normalize(forCountry.json())
    maxCases = data['Cases'].max()
    return trendByCountry(data)



if __name__ == '__main__':
    app.run_server(port=4000,debug=True)