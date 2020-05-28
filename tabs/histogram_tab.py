"""Dash tab for displaying histograms."""

from typing import Dict, List, Union

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
import db
import plotly.graph_objs as go  # type: ignore
from application import app
from dash.dependencies import Input, Output  # type: ignore
from histogram_converter import histogram_to_plotly
from styles import CENTERED_30, CENTERED_100, STAT_LABEL, STAT_NUMBER, WIDTH_30, WIDTH_45


def layout() -> html.Div:
    """Construct the HTML."""
    return html.Div(
        children=[
            html.Div([html.Div([html.H5('Database'),
                                dcc.Dropdown(id='database-name-dropdown-tab1',
                                             value=_get_default_database(),
                                             options=get_database_name_options())],
                               className='two columns',
                               style=WIDTH_45),
                      html.Div([html.H5('Collection'),
                                dcc.Dropdown(id='collection-dropdown-tab1',
                                             value='-')],
                               className='two columns',
                               style=WIDTH_45)
                      ],
                     style=CENTERED_100),

            html.Div([html.Div([
                html.Div(
                    [
                        html.Label(id='filelist-message-tab1',
                                   style=STAT_NUMBER),
                        html.Label('I3Files',
                                   style=STAT_LABEL)
                    ],
                    className='three columns',
                    style=CENTERED_30),
                html.Div(
                    [
                        html.Label(id='n-histogram-message-tab1',
                                   style=STAT_NUMBER),
                        html.Label('Histograms',
                                   style=STAT_LABEL)
                    ],
                    className='three columns',
                    style=CENTERED_30),
                html.Div(
                    [
                        html.Label(id='n-empty-histograms-message-tab1',
                                   style=STAT_NUMBER),
                        html.Label('Empty Histograms',
                                   style=STAT_LABEL)
                    ],
                    className='three columns',
                    style=CENTERED_30),
            ],
                style={'margin-left': '2%'}),
            ],
                style={'margin-top': '3%', 'margin-left': '3%', 'margin-bottom': '9%'}),

            html.Hr(),
            html.Div([html.H3('Histogram'),
                      html.Div([html.Div([dcc.Dropdown(id='histogram-dropdown-tab1',
                                                       value='PrimaryEnergy'),
                                          ],
                                         style=WIDTH_45)
                                ],
                               style=CENTERED_100),
                      html.Div([html.Div(dcc.Graph(id='plot-linear-histogram-tab1'),
                                         className='two columns',
                                         style=WIDTH_45),
                                html.Div(dcc.Graph(id='plot-log-histogram-tab1'),
                                         className='two columns',
                                         style=WIDTH_45)],
                               className='row',
                               style=CENTERED_100)
                      ]),

            html.Hr(),
            html.Div([html.H3('Common Histograms'),
                      html.Div([html.Div([dcc.Graph(id='one-one')],
                                         className='three columns',
                                         style=WIDTH_30),
                                html.Div([dcc.Graph(id='one-two')],
                                         className='three columns',
                                         style=WIDTH_30),
                                html.Div([dcc.Graph(id='one-three')],
                                         className='three columns',
                                         style=WIDTH_30)],
                               className='row',
                               style=CENTERED_100),
                      html.Div([html.Div([dcc.Graph(id='two-one')],
                                         className='three columns',
                                         style=WIDTH_30),
                                html.Div([dcc.Graph(id='two-two')],
                                         className='three columns',
                                         style=WIDTH_30),
                                html.Div([dcc.Graph(id='two-three')],
                                         className='three columns',
                                         style=WIDTH_30)],
                               className='row',
                               style=CENTERED_100),
                      html.Div([html.Div([dcc.Graph(id='three-one')],
                                         className='three columns',
                                         style=WIDTH_30),
                                html.Div([dcc.Graph(id='three-two')],
                                         className='three columns',
                                         style=WIDTH_30),
                                html.Div([dcc.Graph(id='three-three')],
                                         className='three columns',
                                         style=WIDTH_30)],
                               className='row', style=CENTERED_100)
                      ])
        ])


def _get_default_database():
    if len(get_database_name_options()) == 1:
        return get_database_name_options()[0]['label']
    return ''


def get_database_name_options() -> List[Dict[str, str]]:
    """Return the databases available for selection in the dropdown menu."""
    database_names = db.get_database_names()
    return [{'value': n, 'label': n} for n in database_names]


@app.callback(Output('collection-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value')])
def update_collection_options(database_name: str) -> List[Dict[str, str]]:
    """Return the collections available for selection in the dropdown menu."""
    collection_names = db.get_collection_names(database_name)
    return [{'label': name, 'value': name} for name in collection_names]


@app.callback(Output('filelist-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')])
def update_histogram_filelist_message(database_name: str, collection_name: str) -> str:
    """Return number of files in the collection."""
    if not collection_name:
        return ''

    filelist = db.get_filelist(collection_name, database_name)

    i3_files_str = "I3File" if len(filelist) == 1 else "I3Files"
    filelist_message = f"{len(filelist)} {i3_files_str}"

    return f"{len(filelist)}"


@app.callback(Output('n-histogram-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')])
def update_n_histograms_message(database_name: str, collection_name: str) -> str:
    """Return number of histograms in the collection."""
    if not collection_name:
        return ''

    histogram_names = db.get_histogram_names(collection_name, database_name)
    return f"{len(histogram_names)}"


@app.callback(Output('n-empty-histograms-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')])
def update_n_empty_histograms_message(database_name: str, collection_name: str) -> str:
    """Return number of empty histograms in the collection."""
    if not collection_name:
        return ''

    histograms = db.get_histograms(collection_name, database_name,)
    non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
    n_empty = len(histograms) - len(non_empty_histograms)

    return f'{n_empty}'


@app.callback(Output('histogram-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')])
def update_histogram_dropdown_options(database_name: str, collection_name: str) -> Union[None, List[Dict[str, str]]]:
    """Return the histograms available for selection in the dropdown menu."""
    if not collection_name:
        return None

    histograms = db.get_histograms(collection_name, database_name)

    def make_label(h):
        if any(h['bin_values']):
            return h['name']
        return f"{h['name']} (empty)"

    return [{'label': make_label(h), 'value': h['name']} for h in histograms]


@app.callback(
    Output('plot-linear-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_linear_histogram_dropdown(histogram_name: str, database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram(histogram_name, collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('plot-log-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_log_histogram_dropdown(histogram_name: str, database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram(histogram_name, collection_name, database_name)
    return histogram_to_plotly(histogram, log=True)


# NINE PLOTS #


@app.callback(
    Output('one-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_one_one(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('PrimaryEnergy', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('one-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_one_two(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('PrimaryZenith', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('one-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_one_three(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('PrimaryCosZenith', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('two-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_two_one(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('CascadeEnergy', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('two-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_two_two(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('PulseTime', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('two-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_two_three(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('SecondaryMultiplicity', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('three-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_three_one(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('InIceDOMOccupancy', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('three-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_three_two(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('InIceDOMLaunchTime', collection_name, database_name)
    return histogram_to_plotly(histogram)


@app.callback(
    Output('three-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')])
def update_default_histograms_three_three(database_name: str, collection_name: str) -> go.Figure:
    histogram = db.get_histogram('LogQtot', collection_name, database_name)
    return histogram_to_plotly(histogram)
