# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
def create_plot_menu_pane(bindle_stick, start_time, end_time):
    
    query_command = {'timestamp': {'$gt': start_time, '$lt': end_time}}
    
    runs = first_collection.find(query_command)
    
    marks = {i:str(t) if not i%10 else ""
             for i,t in enumerate([r['timestamp'] for r in runs])}
    
    return dcc.RangeSlider(min = 0,
                           max = runs.count(),
                           pushable = 1,
                           marks = marks)



