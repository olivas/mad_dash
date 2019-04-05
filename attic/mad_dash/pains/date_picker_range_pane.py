# -*- coding: utf-8 -*-
import datetime
import dash_core_components as dcc
import dash_html_components as html
def create_date_picker_range_pane(start_date, end_date):
        
    return html.Div([
        html.H6('Date Selection'),
        dcc.DatePickerRange(id = 'date-range',
                            start_date = start_date,
                            end_date = end_date,
                            max_date_allowed = datetime.datetime.now())])

        

