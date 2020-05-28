#!/usr/bin/env python3
"""Mad-Dash application."""

import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
import tabs.comparison_tab as comparison_tab  # type: ignore
import tabs.histogram_tab as histogram_tab  # type: ignore
from application import app
from dash.dependencies import Input, Output  # type: ignore
from styles import CONTENT_STYLE, TAB_SELECTED_STYLE, TAB_STYLE, TABS_STYLE

server = app.server


app.layout = html.Div(
    children=[
        html.Label("Mad Dash", style={'fontSize': 60,
                                      'font-family': 'serif',
                                      'font-weight': '999'}),

        html.Div([dcc.Tabs(id='mad-dash-tabs', value='tab1',
                           children=[
                               dcc.Tab(label='Histograms',
                                       value='tab1',
                                       style=TAB_STYLE,
                                       selected_style=TAB_SELECTED_STYLE),
                               dcc.Tab(label='Comparisons',
                                       value='tab2',
                                       style=TAB_STYLE,
                                       selected_style=TAB_SELECTED_STYLE),
                           ],
                           style=TABS_STYLE),

                  html.Div(id='tab-content', style=CONTENT_STYLE)
                  ],
                 style={'backgroundColor': 'white'}),
    ],
    style={'padding-left': '5%', 'padding-right': '5%', 'backgroundColor': '#FFFFDA'}
)


@app.callback(Output('tab-content', 'children'),
              [Input('mad-dash-tabs', 'value')])
def render_content(tab: str) -> html.Div:
    """Create HTML for tab."""
    layouts = {
        'tab1': histogram_tab.layout,
        'tab2': comparison_tab.layout
    }

    return layouts[tab]()


if __name__ == '__main__':
    app.run_server(debug=True)
