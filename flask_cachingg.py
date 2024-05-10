""" 
from dash import Dash, html, dcc, Input, Output, callback

import datetime as dt

import numpy as np
import pandas as pd
from flask_caching import Cache

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 60


@cache.memoize(timeout=TIMEOUT)
def query_data():
    # This could be an expensive data querying step
    np.random.seed(0)  # no-display
    df = pd.DataFrame(
        np.random.randint(0, 100, size=(100, 4)),
        columns=list('ABCD')
    )
    now = dt.datetime.now()
    df['time'] = [now - dt.timedelta(seconds=5*i) for i in range(100)]
    return df.to_json(date_format='iso', orient='split')


def dataframe():
    return pd.read_json(query_data(), orient='split')


app.layout = html.Div([
    html.Div('Data was updated within the last {} seconds'.format(TIMEOUT)),
    dcc.Dropdown(dataframe().columns, 'A', id='live-dropdown'),
    dcc.Graph(id='live-graph')
])


@callback(Output('live-graph', 'figure'),
          Input('live-dropdown', 'value'))
def update_live_graph(value):
    df = dataframe()
    now = dt.datetime.now()
    return {
        'data': [{
            'x': df['time'],
            'y': df[value],
            'line': {
                'width': 1,
                'color': '#0074D9',
                'shape': 'spline'
            }
        }],
        'layout': {
            # display the current position of now
            # this line will be between 0 and 60 seconds
            # away from the last datapoint
            'shapes': [{
                'type': 'line',
                'xref': 'x', 'x0': now, 'x1': now,
                'yref': 'paper', 'y0': 0, 'y1': 1,
                'line': {'color': 'darkgrey', 'width': 1}
            }],
            'annotations': [{
                'showarrow': False,
                'xref': 'x', 'x': now, 'xanchor': 'right',
                'yref': 'paper', 'y': 0.95, 'yanchor': 'top',
                'text': 'Current time ({}:{}:{})'.format(
                    now.hour, now.minute, now.second),
                'bgcolor': 'rgba(255, 255, 255, 0.8)'
            }],
            # aesthetic options
            'margin': {'l': 40, 'b': 40, 'r': 20, 't': 10},
            'xaxis': {'showgrid': False, 'zeroline': False},
            'yaxis': {'showgrid': False, 'zeroline': False}
        }
    }


if __name__ == '__main__':
    app.run(debug=True)
 """
from dash import Dash, dcc, html, Input, Output, callback

import datetime
from flask_caching import Cache
import pandas as pd
import time
import uuid

external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    # Note that filesystem cache doesn't work on systems with ephemeral
    # filesystems like Heroku.
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
    'CACHE_THRESHOLD': 200
})


def get_dataframe(session_id):
    @cache.memoize()
    def query_and_serialize_data(session_id):
        # expensive or user/session-unique data processing step goes here

        # simulate a user/session-unique data processing step by generating
        # data that is dependent on time
        now = datetime.datetime.now()

        # simulate an expensive data processing task by sleeping
        time.sleep(3)

        df = pd.DataFrame({
            'time': [
                str(now - datetime.timedelta(seconds=15)),
                str(now - datetime.timedelta(seconds=10)),
                str(now - datetime.timedelta(seconds=5)),
                str(now)
            ],
            'values': ['a', 'b', 'a', 'c']
        })
        return df.to_json()

    return pd.read_json(query_and_serialize_data(session_id))


def serve_layout():
    session_id = str(uuid.uuid4())

    return html.Div([
        dcc.Store(data=session_id, id='session-id'),
        html.Button('Get data', id='get-data-button'),
        html.Div(id='output-1'),
        html.Div(id='output-2')
    ])


app.layout = serve_layout


@callback(Output('output-1', 'children'),
          Input('get-data-button', 'n_clicks'),
          Input('session-id', 'data'))
def display_value_1(value, session_id):
    df = get_dataframe(session_id)
    return html.Div([
        'Output 1 - Button has been clicked {} times'.format(value),
        html.Pre(df.to_csv())
    ])


@callback(Output('output-2', 'children'),
          Input('get-data-button', 'n_clicks'),
          Input('session-id', 'data'))
def display_value_2(value, session_id):
    df = get_dataframe(session_id)
    return html.Div([
        'Output 2 - Button has been clicked {} times'.format(value),
        html.Pre(df.to_csv())
    ])


if __name__ == '__main__':
    app.run(debug=True)
