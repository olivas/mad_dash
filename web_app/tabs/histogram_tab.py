"""Dash tab for displaying histograms."""

from typing import Dict, List, Union

import dash_bootstrap_components as dbc  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_daq as daq  # type: ignore
import dash_html_components as html  # type: ignore
import plotly.graph_objs as go  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore

# local imports
import api

from ..config import app
from ..styles import (CENTERED_30, CENTERED_100, HIDDEN, SHORT_HR,
                      STAT_LABEL, STAT_NUMBER, WIDTH_30, WIDTH_45)
from ..utils import db
from ..utils import histogram_converter as hc
from .database_controls import get_database_name_options, get_default_database


def layout() -> html.Div:
    """Construct the HTML."""
    return html.Div(
        children=[
            html.Div(
                style=CENTERED_100,
                children=[
                    html.Div(
                        className='two columns',
                        style=WIDTH_45,
                        children=[
                            html.H6('Database'),
                            dcc.Dropdown(
                                id='database-name-dropdown-tab1',
                                value=get_default_database(),
                                options=get_database_name_options())
                        ]),
                    html.Div(
                        className='two columns',
                        style=WIDTH_45,
                        children=[
                            html.H6('Collection'),
                            dcc.Dropdown(
                                id='collection-name-dropdown-tab1',
                                value='')
                        ])
                ]),

            html.Div(
                id='collection-stats-tab1',
                style=HIDDEN,  # toggled by callback
                children=[
                    html.Div(
                        className='three columns',
                        style=CENTERED_30,
                        children=[
                            html.Label(
                                id='files-number-tab1',
                                style=STAT_NUMBER),
                            html.Label(
                                id='files-label-tab1',
                                style=STAT_LABEL),
                            dbc.Button(
                                'view',
                                id='open-filelist-modal-tab1',
                                size='sm',
                                color='link',
                                style={'vertical-align': 'bottom'}),
                            # Modal of I3Files
                            dbc.Modal(
                                id='filelist-modal-tab1',
                                size='lg',
                                children=[
                                    dbc.ModalHeader(id='filelist-modal-header-tab1'),
                                    dbc.ModalBody(dbc.ListGroup(id='filelist-list-tab1')),
                                    dbc.ModalFooter(
                                        children=[
                                            dbc.Button(
                                                'Close',
                                                id='close-filelist-modal-tab1',
                                                className='ml-auto')
                                        ])
                                ]),
                        ]),
                    html.Div(
                        className='three columns',
                        style=CENTERED_30,
                        children=[
                            html.Label(
                                id='n-histograms-number-tab1',
                                style=STAT_NUMBER),
                            html.Label(
                                id='n-histograms-label-tab1',
                                style=STAT_LABEL)
                        ]),
                    html.Div(
                        className='three columns',
                        style=CENTERED_30,
                        children=[
                            html.Label(
                                id='n-empty-histograms-number-tab1',
                                style=STAT_NUMBER),
                            html.Label(
                                id='n-empty-histograms-label-tab1',
                                style=STAT_LABEL)
                        ]),
                ]),

            html.Hr(),

            html.Div(
                children=[
                    html.H3('Histogram'),
                    html.Div(
                        style=CENTERED_100,
                        children=[
                            html.Div(
                                style=WIDTH_45,
                                children=[
                                    dcc.Dropdown(
                                        id='histogram-dropdown-tab1',
                                        value='PrimaryEnergy')
                                ])
                        ]),
                    html.Div(
                        className='row',
                        style=CENTERED_100,
                        children=[
                            html.Div(dcc.Graph(id='plot-histogram-tab1')),
                            daq.BooleanSwitch(  # pylint: disable=E1101
                                id='toggle-log-tab1',
                                on=False,
                                label='log')
                        ])
                ]),

            html.Hr(),

            html.Div(
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                className='two columns',
                                style=WIDTH_45,
                                children=[
                                    html.H3('Common Histograms')
                                ]),
                            html.Div(
                                className='two columns',
                                style=WIDTH_45,
                                children=[
                                    daq.BooleanSwitch(  # pylint: disable=E1101
                                        id='toggle-log-default-tab1',
                                        on=False,
                                        label='log',
                                        style={'float': 'right'})
                                ])
                        ]),

                    html.Div(
                        className='row',
                        style=CENTERED_100,
                        children=[
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='one-one')
                                ]),
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='one-two')
                                ]),
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='one-three')
                                ])
                        ]),
                    html.Hr(style=SHORT_HR),
                    html.Div(
                        className='row',
                        style=CENTERED_100,
                        children=[
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='two-one')
                                ]),
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='two-two')
                                ]),
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='two-three')
                                ])
                        ]),
                    html.Hr(style=SHORT_HR),
                    html.Div(
                        className='row',
                        style=CENTERED_100,
                        children=[
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='three-one')
                                ]),
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='three-two')
                                ]),
                            html.Div(
                                className='three columns',
                                style=WIDTH_30,
                                children=[
                                    dcc.Graph(id='three-three')
                                ])
                        ])
                ])
        ])


# --------------------------------------------------------------------------------------------------
# Collection Stats


@app.callback(
    Output('collection-stats-tab1', 'style'),
    [Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def hide_show_collection_stats(collection_name: str) -> Dict[str, str]:
    """Hide/show the collection stats div.

    Depends on whether there is a collection selected.
    """
    if not collection_name:
        return HIDDEN
    return {'margin-top': '3%', 'margin-bottom': '9%'}


# --------------------------------------------------------------------------------------------------
# View Files Button and Modal


@app.callback(
    Output('filelist-modal-tab1', 'is_open'),
    [Input('open-filelist-modal-tab1', 'n_clicks'),
     Input('close-filelist-modal-tab1', 'n_clicks')],
    [State('filelist-modal-tab1', 'is_open')])  # type: ignore
def filelist_modal_open_close(n1, n2, is_open):
    """Open/close the filelist modal."""
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output('filelist-modal-header-tab1', 'children'),
    [Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def filelist_modal_header(collection_name: str) -> str:
    """Return header for the filelist modal."""
    return f"Files in {collection_name}"


@app.callback(
    Output('filelist-list-tab1', 'children'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def filelist_modal_list(database_name: str, collection_name: str) -> Union[List[dbc.ListGroupItem], str]:
    """Return list of files for the filelist modal."""
    filelist = db.get_filelist(collection_name, database_name)
    if filelist:
        return [dbc.ListGroupItem(x) for x in filelist]
    return 'None'


# --------------------------------------------------------------------------------------------------
# Collection


@app.callback(Output('collection-name-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value')])  # type: ignore
def update_collection_options(database_name: str) -> List[Dict[str, str]]:
    """Return the collections available for selection in the dropdown menu."""
    collection_names = db.get_collection_names(database_name)
    return [{'label': name, 'value': name} for name in collection_names]


# --------------------------------------------------------------------------------------------------
# N I3Files


@app.callback(Output('files-number-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def update_histogram_filelist_number(database_name: str, collection_name: str) -> str:
    """Return number of files in the collection."""
    filelist = db.get_filelist(collection_name, database_name)

    return str(len(filelist))


@app.callback(Output('files-label-tab1', 'children'),
              [Input('files-number-tab1', 'children')])  # type: ignore
def update_histogram_filelist_label(files: str) -> str:
    """Return label for number of files in the collection."""
    if files == '1':
        return 'I3File'
    return 'I3Files'


# --------------------------------------------------------------------------------------------------
# N Histograms


@app.callback(Output('n-histograms-number-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def update_n_histograms_number(database_name: str, collection_name: str) -> str:
    """Return number of histograms in the collection."""
    histogram_names = db.get_histogram_names(collection_name, database_name)
    return str(len(histogram_names))


@app.callback(Output('n-histograms-label-tab1', 'children'),
              [Input('n-histograms-number-tab1', 'children')])  # type: ignore
def update_n_histograms_label(histos: str) -> str:
    """Return label for number of histograms in the collection."""
    if histos == '1':
        return 'Histogram'
    return 'Histograms'


# --------------------------------------------------------------------------------------------------
# N Empty Histograms


@app.callback(Output('n-empty-histograms-number-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def update_n_empty_histograms_number(database_name: str, collection_name: str) -> str:
    """Return number of empty histograms in the collection."""
    histograms = db.get_histograms(collection_name, database_name,)
    non_empty_histograms = [h for h in histograms if any(h.bin_values)]
    n_empty = len(histograms) - len(non_empty_histograms)

    return str(n_empty)


@app.callback(Output('n-empty-histograms-label-tab1', 'children'),
              [Input('n-empty-histograms-number-tab1', 'children')])  # type: ignore
def update_n_empty_histograms_label(empty_histos: str) -> str:
    """Return label for number of empty histograms in the collection."""
    if empty_histos == '1':
        return 'Empty Histogram'
    return 'Empty Histograms'


# --------------------------------------------------------------------------------------------------
# Histogram Dropdown


@app.callback(Output('histogram-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-name-dropdown-tab1', 'value')])  # type: ignore
def update_histogram_dropdown_options(database_name: str, collection_name: str) -> List[Dict[str, str]]:
    """Return the histograms available for selection in the dropdown menu."""
    if not collection_name:
        return []

    histograms = db.get_histograms(collection_name, database_name)

    def make_label(h: api.I3Histogram) -> str:
        if any(h.bin_values):
            return h.name
        return f"{h.name} (empty)"

    return [{'label': make_label(h), 'value': h.name} for h in histograms]


@app.callback(
    Output('plot-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-tab1', 'on')])  # type: ignore
def update_histogram_dropdown(histogram_name: str, database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot chosen histogram."""
    histogram = db.get_histogram(histogram_name, collection_name, database_name)
    return hc.i3histogram_to_plotly(histogram, y_log=log, no_title=True)


# --------------------------------------------------------------------------------------------------
# Default Histograms


def _plot_default_histogram(database_name: str, collection_name: str, histo_name: str, log: bool) -> go.Figure:
    histogram = db.get_histogram(histo_name, collection_name, database_name)
    return hc.i3histogram_to_plotly(histogram, title=histo_name, alert_no_data=True, y_log=log)


@app.callback(
    Output('one-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_one_one(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'PrimaryEnergy', log)


@app.callback(
    Output('one-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_one_two(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'PrimaryZenith', log)


@app.callback(
    Output('one-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_one_three(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'PrimaryCosZenith', log)


@app.callback(
    Output('two-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_two_one(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'CascadeEnergy', log)


@app.callback(
    Output('two-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_two_two(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'PulseTime', log)


@app.callback(
    Output('two-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_two_three(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'SecondaryMultiplicity', log)


@app.callback(
    Output('three-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_three_one(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'InIceDOMOccupancy', log)


@app.callback(
    Output('three-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_three_two(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'InIceDOMLaunchTime', log)


@app.callback(
    Output('three-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-name-dropdown-tab1', 'value'),
     Input('toggle-log-default-tab1', 'on')])  # type: ignore
def update_default_histograms_three_three(database_name: str, collection_name: str, log: bool) -> go.Figure:
    """Plot a default histogram."""
    return _plot_default_histogram(database_name, collection_name, 'LogQtot', log)
