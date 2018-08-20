# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
def create_generator_selection_pane(db):
    '''
    Gets a list of collections from the database and generates
    a collection selector as a set of radio buttons.
    '''
    collection_names = [n for n in db.collection_names()
                        if n not in ['system.indexes']]

    label_mapping = {'tev_starting_muon': 'TeV Starting Muon',
                     'simple_cascade': 'Simple Cascade',
                     'nugen_numu': 'NuGen NuMu',
                     'nugen_nue': 'NuGen NuE',
                     'nugen_nutau': 'NuGen Tau',
                     'corsika': 'CORSIKA',
                     'corsika_5comp': 'CORSIKA 5 Comp',                     
                     'muon_gun': 'Muon Gun',
    }
    
    options = list()
    for n in collection_names:
        if n in label_mapping:
            options.append({'label': label_mapping[n], 'value': n})
        else:
            options.append({'label': n, 'value': n})
            
    return html.Div([
        html.H6('Generator Selection'),
        dcc.Dropdown(
            id = 'generator_selector',
            options= options,
            value = collection_names,
            multi = True
        )])
        




