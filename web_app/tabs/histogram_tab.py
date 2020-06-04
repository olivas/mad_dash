"""Dash tab for displaying histograms."""

from typing import Dict, List, Union

import dash_bootstrap_components as dbc  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_daq as daq  # type: ignore
import dash_html_components as html  # type: ignore
import plotly.graph_objs as go  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore

from ..config import app
from ..styles import (CENTERED_30, CENTERED_100, SHORT_HR, STAT_LABEL, STAT_NUMBER, WIDTH_30,
                      WIDTH_45)
from ..utils import db, histogram_converter
from .database_controls import get_database_name_options, get_default_database


def layout() -> html.Div:
    """Construct the HTML."""
    return html.Div(
        children=[
            html.Div([html.Div([html.H6('Database'),
                                dcc.Dropdown(id='database-name-dropdown-tab1',
                                             value=get_default_database(),
                                             options=get_database_name_options())],
                               className='two columns',
                               style=WIDTH_45),
                      html.Div([html.H6('Collection'),
                                dcc.Dropdown(id='collection-name-dropdown-tab1',
                                             value='')],
                               className='two columns',
                               style=WIDTH_45)
                      ],
                     style=CENTERED_100),

            html.Div(
                children=[
                    html.Div(
                        [
                            html.Label(id='files-number-tab1',
                                       style=STAT_NUMBER),
                            html.Label(id='files-label-tab1',
                                       style=STAT_LABEL),
                            dbc.Button('view',
                                       id='open-filelist-modal-tab1',
                                       size='sm',
                                       color='link',
                                       style={'vertical-align': 'bottom'}),
                            # Modal of I3Files
                            dbc.Modal([dbc.ModalHeader(id='filelist-modal-header-tab1'),
                                       dbc.ModalBody(dbc.ListGroup(id='filelist-list-tab1')),
                                       dbc.ModalFooter(dbc.Button("Close",
                                                                  id='close-filelist-modal-tab1',
                                                                  className='ml-auto'))
                                       ],
                                      id='filelist-modal-tab1',
                                      size='lg'),
                        ],
                        className='three columns',
                        style=CENTERED_30),
                    html.Div(
                        [
                            html.Label(id='n-histograms-number-tab1',
                                       style=STAT_NUMBER),
                            html.Label(id='n-histograms-label-tab1',
                                       style=STAT_LABEL)
                        ],
                        className='three columns',
                        style=CENTERED_30),
                    html.Div(
                        [
                            html.Label(id='n-empty-histograms-number-tab1',
                                       style=STAT_NUMBER),
                            html.Label(id='n-empty-histograms-label-tab1',
                                       style=STAT_LABEL)
                        ],
                        className='three columns',
                        style=CENTERED_30),
                ],
                id='collection-stats-tab1'),



            html.Hr(),
            html.Div([html.H3('Histogram'),
                      html.Div([html.Div([dcc.Dropdown(id='histogram-dropdown-tab1',
                                                       value='PrimaryEnergy'),
                                          ],
                                         style=WIDTH_45)
                                ],
                               style=CENTERED_100),
                      html.Div([html.Div(dcc.Graph(id='plot-histogram-tab1')),
                                daq.BooleanSwitch(id='toggle-log-tab1',
                                                  on=False,
                                                  label='log')
                                ],
                               className='row',
                               style=CENTERED_100)
                      ]),

            html.Hr(),
            html.Div(
                children=[
                    html.Div([html.Div(html.H3('Common Histograms'),
                                       className='two columns',
                                       style=WIDTH_45),
                              html.Div(daq.BooleanSwitch(id='toggle-log-common-tab1',
                                                         on=False,
                                                         label='log',
                                                         style={'float': 'right'}),
                                       className='two columns',
                                       style=WIDTH_45)],
                             className='row'),

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
                    html.Hr(style=SHORT_HR),
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
                    html.Hr(style=SHORT_HR),
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


# --------------------------------------------------------------------------------------------------
# Collection Stats


@app.callback(
    Output('collection-stats-tab1', 'style'),
    [Input('collection-name-dropdown-tab1', 'value')])
def hide_show_collection_stats(collection_name: str) -> dict:
    """Hide/show the collection stats div, depending on whether there is a collection selected."""
    if not collection_name:
        return {'visibility': 'hidden'}
    return {'margin-top': '3%', 'margin-bottom': '9%'}


# --------------------------------------------------------------------------------------------------
# View Files Button and Modal


@app.callback(
    Output('filelist-modal-tab1', 'is_open'),
    [Input('open-filelist-modal-tab1', 'n_clicks'),
     Input('close-filelist-modal-tab1', 'n_clicks')],
    [State('filelist-modal-tab1', 'is_open')])
def filelist_modal_open_close(n1, n2, is_open):
    """Open/close the filelist modal."""
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output('filelist-modal-header-tab1', 'children'),
    [Input('collection-name-dropdown-tab1', 'value')])
def filelist_modal_header(collection_name: str) -> str:
    """Return header for the filelist modal."""
    return f"Files in {collection_name}"


@app.callback(
    Output('filelist-list-tab1', 'children'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value')])
def filelist_modal_list(database_name: str, collection_name: str) -> Union[List[dbc.ListGroupItem], str]:
    """Return list of files for the filelist modal."""
    filelist = db.get_filelist(collection_name, database_name)
    if filelist:
        return [dbc.ListGroupItem(x) for x in filelist]
    return 'None'


# --------------------------------------------------------------------------------------------------
# Collection


@app.callback(Output('collection-name-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value')])
def update_collection_options(database_name: str) -> List[Dict[str, str]]:
    """Return the collections available for selection in the dropdown menu."""
    collection_names = db.get_collection_names(database_name)
    return [{'label': name, 'value': name} for name in collection_names]


# --------------------------------------------------------------------------------------------------
# N I3Files


@app.callback(Output('files-number-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])
def update_histogram_filelist_number(database_name: str, collection_name: str) -> str:
    """Return number of files in the collection."""
    filelist = db.get_filelist(collection_name, database_name)

    return str(len(filelist))


@app.callback(Output('files-label-tab1', 'children'),
              [Input('files-number-tab1', 'children')])
def update_histogram_filelist_label(files: str) -> str:
    """Return label for number of files in the collection."""
    if files == '1':
        return 'I3File'
    return 'I3Files'


# --------------------------------------------------------------------------------------------------
# N Histograms


@app.callback(Output('n-histograms-number-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])
def update_n_histograms_number(database_name: str, collection_name: str) -> str:
    """Return number of histograms in the collection."""
    histogram_names = db.get_histogram_names(collection_name, database_name)
    return str(len(histogram_names))


@app.callback(Output('n-histograms-label-tab1', 'children'),
              [Input('n-histograms-number-tab1', 'children')])
def update_n_histograms_label(histos: str) -> str:
    """Return label for number of histograms in the collection."""
    if histos == '1':
        return 'Histogram'
    return 'Histograms'


# --------------------------------------------------------------------------------------------------
# N Empty Histograms


@app.callback(Output('n-empty-histograms-number-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])
def update_n_empty_histograms_number(database_name: str, collection_name: str) -> str:
    """Return number of empty histograms in the collection."""
    histograms = db.get_histograms(collection_name, database_name,)
    non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
    n_empty = len(histograms) - len(non_empty_histograms)

    return str(n_empty)


@app.callback(Output('n-empty-histograms-label-tab1', 'children'),
              [Input('n-empty-histograms-number-tab1', 'children')])
def update_n_empty_histograms_label(empty_histos: str) -> str:
    """Return label for number of empty histograms in the collection."""
    if empty_histos == '1':
        return 'Empty Histogram'
    return 'Empty Histograms'


# --------------------------------------------------------------------------------------------------
# Histogram Dropdown


@app.callback(Output('histogram-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])
def update_histogram_dropdown_options(database_name: str, collection_name: str) -> List[Dict[str, str]]:
    """Return the histograms available for selection in the dropdown menu."""
    if not collection_name:
        return []

    histograms = db.get_histograms(collection_name, database_name)

    def make_label(h):
        if any(h['bin_values']):
            return h['name']
        return f"{h['name']} (empty)"

    return [{'label': make_label(h), 'value': h['name']} for h in histograms]


@app.callback(
    Output('plot-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-tab1', 'on')])
def update_linear_histogram_dropdown(histogram_name: str, database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot chosen histogram."""
    histogram = db.get_histogram(histogram_name, collection_name, database_name)
    return histogram_converter.histogram_to_plotly(histogram, y_log=log, no_title=True)


# --------------------------------------------------------------------------------------------------
# Common Histograms


def _plot_histogram(database_name: str, collection_name: str, histo_name: str, log: bool) -> go.Figure:
    histogram = db.get_histogram(histo_name, collection_name, database_name)
    return histogram_converter.histogram_to_plotly(histogram, title=histo_name, alert_no_data=True, y_log=log)


@app.callback(
    Output('one-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_one_one(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'PrimaryEnergy', log)


@app.callback(
    Output('one-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_one_two(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'PrimaryZenith', log)


@app.callback(
    Output('one-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_one_three(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'PrimaryCosZenith', log)


@app.callback(
    Output('two-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_two_one(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'CascadeEnergy', log)


@app.callback(
    Output('two-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_two_two(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'PulseTime', log)


@app.callback(
    Output('two-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_two_three(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'SecondaryMultiplicity', log)


@app.callback(
    Output('three-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_three_one(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'InIceDOMOccupancy', log)


@app.callback(
    Output('three-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_three_two(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'InIceDOMLaunchTime', log)


@app.callback(
    Output('three-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-common-tab1', 'on')])
def update_default_histograms_three_three(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a common histogram."""
    return _plot_histogram(database_name, collection_name, 'LogQtot', log)
