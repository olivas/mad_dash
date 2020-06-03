# -*- coding: utf-8 -*-
from copy import copy
# from statistics.compare import compare
from typing import Dict, List

import dash_core_components as dcc  # type: ignore
import dash_daq as daq  # type: ignore
import dash_html_components as html  # type: ignore
import plotly.graph_objs as go  # type: ignore
from dash.dependencies import Input, Output, State

from ..config import app
from ..styles import (CENTERED_30, CENTERED_100, SHORT_HR, STAT_LABEL, STAT_NUMBER, WIDTH_30,
                      WIDTH_45)
from ..utils import db, histogram_converter
from .database_controls import get_database_name_options, get_default_database


def cdf(histogram):
    cdf_histogram = copy(histogram)
    v = 0
    for idx, bv in enumerate(histogram['bin_values']):
        v += bv
        histogram['bin_values'][idx] = v
    return histogram


def scale_to_match(h1, h2):

    n1 = sum(h1['bin_values'])
    n2 = sum(h2['bin_values'])

    if n1 == 0 or n2 == 0:
        return

    print('before sum1 = %d' % sum(h1['bin_values']))
    print('before sum2 = %d' % sum(h2['bin_values']))

    if n1 > n2:
        N = n1 / n2
        print('N = %d' % N)
        for idx in range(len(h1['bin_values'])):
            h1['bin_values'][idx] /= N
    else:
        N = n2 / n1
        print('N = %d' % N)
        for idx in range(len(h2['bin_values'])):
            h2['bin_values'][idx] /= N

    print('after sum1 = %d' % sum(h1['bin_values']))
    print('after sum2 = %d' % sum(h2['bin_values']))


def layout() -> html.Div:
    """Construct the HTML."""
    return html.Div([


        html.Div([html.H6('Database'),
                  dcc.Dropdown(id='database-name-dropdown-tab2',
                               value=get_default_database(),
                               options=get_database_name_options())],
                 style=WIDTH_45),


        html.Hr(),

        html.Div([html.H6('Collections'),
                  dcc.Dropdown(id='collections-dropdown-tab2',
                               multi=True)
                  ]),

        html.Hr(),

        html.Div([html.H3('Histogram Comparisons'),
                  html.Div([html.Div([dcc.Dropdown(id='histogram-dropdown-tab2')],
                                     style=WIDTH_45)],
                           style=CENTERED_100),

                  html.Div([html.Div(dcc.Graph(id='plot-histogram-tab2')),
                            daq.ToggleSwitch(id='toggle-log-tab2',
                                             value=False,
                                             label='log')
                            ],
                           className='row',
                           style=CENTERED_100),
                  html.Hr(style=SHORT_HR),
                  html.Div([html.Div(dcc.Graph(id='plot-histogram-ratio-tab2'),
                                     className='two columns',
                                     style=WIDTH_45),
                            html.Div(dcc.Graph(id='plot-histogram-cdf-tab2'),
                                     className='two columns',
                                     style=WIDTH_45)],
                           className='row'),
                  ]),

        html.Hr(),
        html.Table(id='collection-comparison-result-tab2'),
    ])


# --------------------------------------------------------------------------------------------------
# Collections

def _collection_options(database_name: str) -> List[Dict[str, str]]:
    collection_names = db.get_collection_names(database_name)
    options = [{'label': name, 'value': name} for name in collection_names]

    return options


@app.callback(Output('collections-dropdown-tab2', 'options'),
              [Input('database-name-dropdown-tab2', 'value')])
def set_lhs_collection_options(database_name: str) -> List[Dict[str, str]]:
    return _collection_options(database_name)


# --------------------------------------------------------------------------------------------------
# Histograms


@app.callback(Output('histogram-dropdown-tab2', 'options'),
              [Input('database-name-dropdown-tab2', 'value'),
               Input('collections-dropdown-tab2', 'value')])
def update_histogram_dropdown_options(database_name: str, collection_names: List[str]) -> List[Dict[str, str]]:
    if not collection_names:
        collection_names = []

    all_histogram_names = [db.get_histogram_names(c, database_name) for c in collection_names]

    # get common histogram names
    sets_of_names = [set(names) for names in all_histogram_names]
    if not any(sets_of_names):
        return []
    histogram_names = sorted(set.intersection(*sets_of_names))

    return [{'label': name, 'value': name} for name in histogram_names]


@app.callback(
    Output('plot-histogram-tab2', 'figure'),
    [Input('histogram-dropdown-tab2', 'value'),
     Input('toggle-log-tab2', 'value'),
     Input('database-name-dropdown-tab2', 'value'),
     Input('collections-dropdown-tab2', 'value')])
def update_histogram_dropdown(histogram_name: str, log: bool, database_name: str, collection_names: List[str]) -> go.Figure:
    if not collection_names:
        collection_names = []

    all_histograms = [db.get_histogram(histogram_name, c, database_name) for c in collection_names]

    return histogram_converter.n_histograms_to_plotly(all_histograms, y_log=log, no_title=True)


# @app.callback(
#     Output('plot-histogram-ratio-tab2', 'figure'),
#     [Input('histogram-dropdown-tab2', 'value')],
#     [State('database-name-dropdown-tab2', 'value'),
#      State('collections-dropdown-tab2', 'value')])
# def update_ratio_histogram(histogram_name: str, database_name: str, collection_names: List[str]) -> go.Figure:
#     if not collection_names:
#         return go.Figure()

# all_histograms = [db.get_histogram(histogram_name, c, database_name) for
# c in collection_names]

#     scale_to_match(all_histograms)

#     ratio_histogram = copy(lhs_histogram)
#     for idx, bv in enumerate(rhs_histogram['bin_values']):
#         ratio_histogram['bin_values'][idx] /= bv if bv > 0 else 1.

#     return histogram_converter.histogram_to_plotly(ratio_histogram, title="Scaled to Match Ratio")


# @app.callback(
#     Output('plot-histogram-cdf-tab2', 'figure'),
#     [Input('histogram-dropdown-tab2', 'value')],
#     [State('database-name-dropdown-tab2', 'value'),
#      State('collections-dropdown-tab2', 'value')])
# def update_cdf_histogram(histogram_name: str, database_name: str, collection_names: List[str]) -> go.Figure:
#     if not collection_names:
#         return go.Figure()

#     lhs_histogram = db.get_histogram(histogram_name, collection_names[0], database_name)
#     rhs_histogram = db.get_histogram(histogram_name, collection_names[1], database_name)

#     scale_to_match(all_histograms)

#     ratio_histogram = cdf(lhs_histogram)
#     for idx, bv in enumerate(cdf(rhs_histogram)['bin_values']):
#         ratio_histogram['bin_values'][idx] /= bv if bv > 0 else 1.

# return histogram_converter.histogram_to_plotly(ratio_histogram,
# title="Scaled to Match CDF Ratio")


# --------------------------------------------------------------------------------------------------
# Comparison Table


@app.callback(Output('collection-comparison-result-tab2', 'children'),
              [Input('database-name-dropdown-tab2', 'value'),
               Input('collections-dropdown-tab2', 'value')])
def compare_collections(database_name: str, collection_names: List[str]) -> List[html.Tr]:
    if not collection_names:
        collection_names = []

    print("compare_collections: Comparing...")
    headers = ['Histogram', 'Chi2', 'KS', 'AD', 'Result', 'Notes']
    table_elements = [html.Tr([html.Th(h) for h in headers])]

    # def extract_histograms(database_name: str, collection_name: str) -> Dict[str, str]:
    #     histograms = db.get_histograms(collection_name, database_name)
    #     return {h['name']: h for h in histograms} if histograms else dict()

    # lhs_histograms = extract_histograms(database_name, collection_names[0])
    # rhs_histograms = extract_histograms(database_name, collection_names[1])

    # results = dict()
    # for lhs_name, lhs_histogram in lhs_histograms.items():
    #     if lhs_name not in rhs_histograms:
    #         print("Histogram %s in LHS, but not RHS." % lhs_name)
    #         continue
    #     rhs_histogram = rhs_histograms[lhs_name]
    #     results[lhs_name] = compare(lhs_histogram, rhs_histogram)

    # headers = ['Histogram', 'Chi2', 'KS', 'AD', 'Result', 'Notes']
    # table_elements = [html.Tr([html.Th(h) for h in headers])]
    # for name, result in results.items():
    #     chi2_result = result['chisq']['pvalue'] if 'chisq' in result else '---'
    #     KS_result = result['KS']['pvalue'] if 'KS' in result else '---'
    #     AD_result = result['AD']['pvalue'] if 'AD' in result else '---'
    #     pass_fail = 'PASS'
    #     notes = 'N/A'

    #     if 'chisq' not in result and 'KS' not in result and 'AD' not in result:
    #         if len(result) == 1:
    #             notes = list(result.keys())[0]

    #     row_data = [name, str(chi2_result), KS_result, AD_result, pass_fail, notes]
    #     row = html.Tr([html.Td(d) for d in row_data])
    #     table_elements.append(row)

    print("compare_collections: Done.")
    return table_elements
