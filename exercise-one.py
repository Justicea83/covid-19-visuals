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
    #trace1 = go.Bar(x=df['NOC'],y=df['Gold'],name='Gold',marker=dict(color = '#FFD700'))
    trace1 = go.Bar(y=df['Date'],x=df['Cases'],name='Confirmed',orientation='h')
    #trace2 = go.Bar(y=df['Date'],x=df['Deaths'],name='Deaths',orientation='h')
    #trace3 = go.Bar(y=df['Date'],x=df['Recovered'],name='Recovered',orientation='h')
    #trace4 = go.Bar(y=df['Date'],x=df['Active'],name='Active',orientation='h')


    data = [trace1]
    # for row in forCountry.iterrows():
    #     trace = 

    layout = go.Layout(title='Country Trend Analysis',xaxis=dict(title= 'Date'),yaxis=dict(title = 'Cases'),barmode='stack')
    return go.Figure(data=data,layout=layout)
    

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
    html.P('Total Percentage of People with Covid 19',id='percentage-value')

    ],className='appWrapper')
],className='app')

#callbacks
@app.callback(
    Output(component_id='percentage-value', component_property='children'),
    [Input(component_id='country-dropdown', component_property='value')]
)
def update_output_div(input_value):
    selected_country = countryDf[countryDf['Slug'] == input_value]
    url = "http://api.worldbank.org/v2/country/{}/indicator/SP.POP.TOTL?format=json".format(selected_country['ISO2'].iloc[0])

    print(url)
    req = requests.get(url)
    
    print(req.text)
    #data = json_normalize(req.json())
    #print(data[0])
    return input_value


@app.callback(
    Output(component_id='country-trend', component_property='figure'),
    [Input(component_id='country-dropdown', component_property='value')]
)
def update_output_div(input_value):
   # forCountry = requests.get("https://api.covid19api.com/live/country/{}".format(input_value))
    forCountry = requests.get("https://api.covid19api.com/country/{}/status/confirmed/live".format(input_value))
    data = json_normalize(forCountry.json())
    return trendByCountry(data)



if __name__ == '__main__':
    app.run_server(port=4000,debug=True)