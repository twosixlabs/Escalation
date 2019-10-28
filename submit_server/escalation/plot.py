import json
import operator

from collections import defaultdict
from flask import current_app as app
import numpy as np
import plotly.graph_objs as go
import plotly
from sqlalchemy import text, func

from escalation import db
from escalation.database import get_chemicals, get_leaderboard, get_feature_analysis, get_features, get_leaderboard_loo_inchis
from escalation.database import TrainingRun

global plot_data

plot_data = defaultdict(dict)

def update_success_by_amine():
    """ Update "Success Rate by Amine" plot in the Science tab and overview tab
        Adds successes and total experiments for each amine to plot_data['success_by_amine']
    """
    global plot_data
    name = 'success_by_amine'

    chemicals = {}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name

    rows = db.session.query(TrainingRun.name,
                                 TrainingRun.inchikey,
                                 TrainingRun._out_crystalscore,
                                 TrainingRun._rxn_M_organic,
                                 TrainingRun._rxn_M_inorganic,
                                 TrainingRun._rxn_M_acid,
                                 TrainingRun._rxn_temperatureC_actual_bulk).distinct().all()
    
    total = defaultdict(int)
    success = defaultdict(int)
    for r in rows:
        total[r.inchikey] += 1
        if r._out_crystalscore == 4:
            success[r.inchikey] += 1

    sorted_amine = [x[0] for x in sorted(total.items(), key=operator.itemgetter(1))]
    plot_data[name]['xs'] = [chemicals[amine] if amine in chemicals else amine for amine in sorted_amine]
    plot_data[name]['ys_success'] = [success[amine] for amine in sorted_amine]
    plot_data[name]['ys_total'] = [total[amine] for amine in sorted_amine]
    #app.logger.info(plot_data)


def success_by_amine():
    """ Generates plotly figure "Success Rate by Amine" plot in the Science tab 
        based on data recieved from update_success_by_amine()
        Returns:
            json object representing plotly figure
    """
    global plot_data
    name = 'success_by_amine'

    if name not in plot_data:
        update_success_by_amine()

    trace1 = go.Bar(
        x=plot_data[name]['xs'],
        y=plot_data[name]['ys_success'],
        name="Successes",
        marker={
            'color': '#5eabdb'
        }
    )
    trace2 = go.Bar(
        x=plot_data[name]['xs'],
        y=plot_data[name]['ys_total'],
        name="Total",
        marker={
            'color': '#a55942'
        }
    )
    layout = go.Layout(
        xaxis={'title': "<b>Ammonium Iodide Salt</b>",
               'automargin': True
               },
        yaxis={'title': "<b>Number of Experiments</b>"},
        title="<b>Success Rate by Amine</b>",
    )
    graph = {'data': [trace1, trace2],
             'layout': layout
             }
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


def update_runs_by_crank():
    """ Updates "Total Experiments by Time" plot in the automation and overview tab
        Adds total number of experiments and successes vs. time to plot_data['runs_by_crank']
    """
    global plot_data
    name = 'runs_by_crank'
    app.logger.info("Updating %s" % (name))
    total = defaultdict(int)
    success = defaultdict(int)

    rows = db.session.query(TrainingRun.dataset, 
                             func.count(TrainingRun._out_crystalscore).label('count')).\
                      group_by(TrainingRun.dataset).all()
    
    for row in rows:
        total[row.dataset] = row.count
    rows = db.session.query(TrainingRun.dataset, 
                             func.count(TrainingRun._out_crystalscore).label('count')).\
                             filter(TrainingRun._out_crystalscore==4).group_by(TrainingRun.dataset).all()
    for row in rows:
        success[row.dataset] = row.count
    
    sorted_list = sorted(total.keys())  # [x[0] for x in sorted(total.items(), key=operator.itemgetter(1)) ]
    plot_data[name]['xs'] = [crank for crank in sorted_list]
    plot_data[name]['ys_success'] = [success[crank] for crank in sorted_list]
    plot_data[name]['ys_total'] = [total[crank] for crank in sorted_list]


def runs_by_crank():
    """Generates plotly figure "Total Experiments by Time" plot in the automation and overview tab
        based on data recieved from update_runs_by_crank()
        Returns:
            json object representing plotly figure
    """
    global plot_data
    name = 'runs_by_crank'

    if name not in plot_data:
        update_runs_by_crank()

    trace1 = go.Scatter(
        x=plot_data[name]['xs'],
        y=plot_data[name]['ys_total'],
        mode='lines',
        name="Total",
        marker={
            'color': '#a55942',
        }
    )
    trace2 = go.Scatter(
        x=plot_data[name]['xs'],
        y=plot_data[name]['ys_success'],
        mode='lines',
        name="Successes",
        marker={
            'color': '#5eabdb',
        }
    )
    layout = go.Layout(
        xaxis={'title': "<b>Progress By Weekly Crank</b>",
               'automargin': True,
               'showgrid': False,
               },
        yaxis={'title': "<b>Number of Experiments</b>",
               'range': [0, 1000 * (1 + max(plot_data[name]['ys_total']) // 1000)],
               'showgrid': False,
               },
        title="<b>Total Number of Experiments over Time</b>",
    )
    graph = {'data': [trace1, trace2],
             'layout': layout
             }
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


def update_runs_by_month():
    """ Updates "Number of Experiments by Month" plot in the automation tab
        Adds total number of experiments per amine vs. month to plot_data['runs_by_month']
    """
    global plot_data
    name = 'runs_by_month'
    app.logger.info("Updating %s" % (name))
    if name not in plot_data:
        update_runs_by_crank()

    total = defaultdict(int)
    success = defaultdict(int)

    rows = db.session.query(TrainingRun.name, TrainingRun.inchikey).distinct().all()
    #print(len(rows))

    xs = set()
    by_inchi = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    for row in rows:
        #by_inchi[row[1]][row[0][:7]] += 1
        by_inchi[row.inchikey][row.name[:7]] += 1
        xs.add(row.name[:7])
        totals[row.inchikey] += 1

    xs = sorted(list(xs))
    ys_dict = {}
    monthy = defaultdict(int)
    sorted_inchis = [x[0] for x in sorted(totals.items(), key=operator.itemgetter(1), reverse=True)]
    for inchi in sorted_inchis:
        ys = []

        for month in xs:
            ys.append(by_inchi[inchi][month])
            monthy[month] += by_inchi[inchi][month]
        ys_dict[inchi] = ys

    max_y = 0
    for month, y in monthy.items():
        if y > max_y:
            max_y = y

    plot_data[name]['xs'] = xs
    plot_data[name]['ys'] = ys_dict
    plot_data[name]['ymax'] = max_y


def runs_by_month():
    """Generates plotly figure "Number of Experiments by Month" plot in the automation tab
        based on data recieved from update_runs_by_month()
        Returns:
            json object representing plotly figure
    """
    global plot_data
    name = 'runs_by_month'

    chemicals = {}
    abbrev = {}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name
        abbrev[r.inchi] = r.abbrev

    if name not in plot_data:
        update_runs_by_month()

    trace = []
    for inchi, ys in plot_data[name]['ys'].items():
        chem = chemicals[inchi] if inchi in chemicals else inchi
        abb = abbrev[inchi] if inchi in chemicals else inchi[:7]
        trace.append(go.Bar(
            x=plot_data[name]['xs'],
            y=ys,
            text=["%d %s" % (y, abb) for y in ys],
            name=chem,
            hoverlabel=dict(namelength=-1),
            hoverinfo='text',
            marker={'color': ['#5eabdb' for x in plot_data[name]['xs']],
                    'line': {'color': '#000000', 'width': 1},
                    }
        ))

    layout = go.Layout(
        xaxis={'title': "<b>Progress By Month</b>",
               'automargin': True,
               'showgrid': False,
               'tickangle': 45,
               },
        yaxis={'title': "<b>Number of Experiments</b>",
               'range': [0, 100 * (1 + plot_data[name]['ymax'] // 100)],
               'showgrid': False,
               },
        title="<b>Number of Experiments per Month</b>",
        barmode='stack',
        hovermode='closest',
        showlegend=False,
    )
    graph = {'data': trace,
             'layout': layout
             }
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


def update_results_by_model(loo=True):
    """Updates ML metrics in ML tab
        Adds different metrics into plot_data['results_by_model_*'] based on what is selected

    Args:
        loo (bool): Switches between leave-one-out and regular stats
    
    """
    if loo:
        name = 'results_by_model_loo'
    else:
        name = 'results_by_model_all'
        
    app.logger.info("Updating %s" % (name))
    global plot_data

    chemicals = {}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name
    
    res = get_leaderboard(loo)

    results = defaultdict(list)

    # first group the data together by model
    for r in res:
        if 'auc' in r:
            results[r['model']].append(r)

    # sort array of rows by their dataset name
    for m in results:
        results[m] = sorted(results[m], key=lambda x: x['crank'])

    d_f1       = defaultdict(list)
    d_auc      = defaultdict(list)
    d_avg_prec = defaultdict(list)
    d_prec     = defaultdict(list)
    d_rec      = defaultdict(list)
    d_dataset  = defaultdict(list)
    d_inchi    = defaultdict(list)

    
    # now we hav a sorted dict of numbers by model
    for m in results:
        d_f1[m]       = [x['f1'] for x in results[m]]
        d_auc[m]      = [x['auc'] for x in results[m]]
        d_avg_prec[m] = [x['avgp'] for x in results[m]]
        d_rec[m]      = [x['recall'] for x in results[m]]
        d_prec[m]     = [x['prec'] for x in results[m]]
        d_dataset[m]  = [x['crank'] for x in results[m]]
        d_inchi[m]    = [chemicals[x['inchi']] if x['inchi'] in chemicals else x['inchi'] for x in results[m]]

    plot_data[name]['f1']       = []
    plot_data[name]['auc']      = []
    plot_data[name]['avg_prec'] = []
    plot_data[name]['model']    = []
    plot_data[name]['prec']     = []
    plot_data[name]['rec']      = []
    plot_data[name]['dataset']  = []
    plot_data[name]['inchi']    = []

    # sort models by their means
    means = defaultdict(float)
    for model, arr in d_auc.items():
        means[model] = sum(arr) / len(arr)
    sorted_models = [x[0] for x in sorted(means.items(), key=operator.itemgetter(1), reverse=False)]

    for model in sorted_models:
        plot_data[name]['model'].append(model)
        plot_data[name]['f1'].append(d_f1[model])
        plot_data[name]['auc'].append(d_auc[model])
        plot_data[name]['rec'].append(d_rec[model])
        plot_data[name]['prec'].append(d_prec[model])
        plot_data[name]['avg_prec'].append(d_avg_prec[model])
        plot_data[name]['dataset'].append(d_dataset[model])
        plot_data[name]['inchi'].append(d_inchi[model])        

def results_by_model(loo=True):
    """Generates plotly plot to show different ML metrics

    Args:
        loo (bool) : Switches between leave-one-out and regular stats
    
    Returns:
        json object representing plotly figure

    """
    if loo:
        name = 'results_by_model_loo'
    else:
        name = 'results_by_model_all'

    global plot_data

    if name not in plot_data:
        update_results_by_model(loo)

    models = plot_data[name]['model']
    f1_trace = []
    auc_trace = []
    prec_trace = []

    for i, model in enumerate(models):

        if loo:
            text = plot_data[name]['inchi'][i]
        else:
            text=[]
        auc_trace.append(go.Box(
            x=plot_data[name]['auc'][i],
            name=model,
            visible=True,
            boxpoints='all',
            pointpos=0,
            marker={'size':7},
            hovertext=text,
            hoverinfo="text",
        ))

        f1_trace.append(go.Box(
            x=plot_data[name]['f1'][i],
            name=model,
            visible=False,
            boxpoints='all',            
            pointpos=0,
            marker={'size':7},
            hovertext=text,
            hoverinfo="text",
        ))

        prec_trace.append(go.Box(
            x=plot_data[name]['avg_prec'][i],
            name=model,
            visible=False,
            boxpoints='all',
            pointpos=0,
            marker={'size':7},
            hovertext=text,
            hoverinfo="text",
        ))
    auc_bools = [True] * len(models) + [False] * (2 * len(models))
    f1_bools = [False] * len(models) + [True] * len(models) + [False] * len(models)
    prec_bools = [False] * (2 * len(models)) + [True] * len(models)

    number_of_cranks = 0
    number_of_inchis = len(get_leaderboard_loo_inchis())
    if plot_data[name]['auc']:
        number_of_cranks = len(plot_data[name]['auc'][0])
    if loo:
        prefix = 'Leave-One-Out'
        number_of_cranks = 1
    else:
        prefix = 'K-Fold'

    layout = go.Layout(
        xaxis={'title': '<b>AUC</b>',
               'range': [0.5, 1],
               'tick0': 0.5,
               'dtick': 0.05,
               'ticklen': 10,
               'showgrid': True,
               },
        yaxis={'automargin': True,
               'title': '<b>Classifier</b>',
               },
        title="<b>%s AUC scores over %d cranks and %d chemicals</b>" % (prefix, number_of_cranks, number_of_inchis),
        showlegend=False,
        updatemenus=list([
            dict(
                buttons=list([
                    dict(label='AUC',
                         method='update',
                         args=[{'visible': auc_bools},
                               {'title': "<b>%s AUC scores over %d cranks and %d chemicals</b>" % (prefix, number_of_cranks, number_of_inchis),
                                'xaxis': {'title': '<b>AUC</b>',
                                          'range': [0.5, 1],
                                          'tick0': 0.5,
                                          'dtick': 0.05,
                                          'ticklen': 10,
                                          'showgrid': True,
                                          }},
                               ]),
                    dict(label='Avg. Prec',
                         method='update',
                         args=[{'visible': prec_bools},
                               {'title': "<b>%s Average Precision over %d cranks and %d chemicals</b>" % (prefix, number_of_cranks, number_of_inchis),
                                'xaxis': {'title': '<b>Average Precision</b>',
                                          'range': [0, 1],
                                          'tick0': 0,
                                          'dtick': 0.1,
                                          'ticklen': 10,
                                          'showgrid': True,
                                          }},
                               ]),
                    dict(label='F1 Score',
                         method='update',
                         args=[{'visible': f1_bools},
                               {'title': "<b>%s F1 scores over %d cranks and %d chemicals</b>" % (prefix, number_of_cranks, number_of_inchis),
                                'xaxis': {'title': '<b>F1 Score</b>',
                                          'range': [0, 1],
                                          'tick0': 0,
                                          'dtick': 0.1,
                                          'ticklen': 10,
                                          'showgrid': True,
                                          }},
                               ]
                         ),
                ]),
                direction='right',
                showactive=True,
                type='buttons',
                y=1.4,
                yanchor='top'
            )
        ]),
    )
    graph = {'data': auc_trace + f1_trace + prec_trace, 'layout': layout}
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


def f1_by_model(loo = True):
    """Generates plotly plot to show different ML metrics

    Args:
        loo (bool) : Switches between leave-one-out and regular stats
    
    Returns:
        json object representing plotly figure

    """
    global plot_data
    if loo:
        name = 'results_by_model_loo'
    else:
        name = 'results_by_model_all'

    # uses the same update function as above
    if name not in plot_data:
        update_results_by_model(loo)

    models = plot_data[name]['model']
    colors = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'  # blue-teal
    ]

    trace = []
    shapes = []
    for i, model in enumerate(models):
        trace.append(go.Scatter(
            x=plot_data[name]['prec'][i],
            y=plot_data[name]['rec'][i],
            text=plot_data[name]['dataset'][i],
            name=model,
            mode='markers',
            marker=dict(size=12,
                        color=colors[i],
                        )
        ))
        # shapes.append(
        #     {
        #         'type': 'circle',
        #         'xref': 'x',
        #         'yref': 'y',
        #         'x0': min(plot_data[name]['prec'][i]),
        #         'x1': max(plot_data[name]['prec'][i]),                
        #         'y0': min(plot_data[name]['rec'][i]),
        #         'y1': max(plot_data[name]['rec'][i]),
        #         'opacity': 0.2,
        #         'fillcolor': colors[i],
        #     }
        # )

    layout = go.Layout(
        autosize=False,
        width=1000,
        height=600,
        xaxis={'title': '<b>Precision</b>',
               'range': [0, 1],
               'tick0': 0,
               'dtick': 0.1,
               'ticklen': 10,
               'showgrid': True,
               },
        yaxis={
            'title': '<b>Recall</b>',
            'range': [0, 1],
            'tick0': 0,
            'dtick': 0.1,
            'ticklen': 10,
            'showgrid': True,
        },
        title="<b>Precision and Recall</b>",
        showlegend=True,
        #        shapes=shapes,
    )

    graph = {'data': trace, 'layout': layout}
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


def results_by_crank(loo=True):
    """Generates plotly plot to show different ML metrics

    Args:
        loo (bool) : Switches between leave-one-out and regular stats
    
    Returns:
        json object representing plotly figure

    """
    global plot_data

    if loo:
        name = 'results_by_model_loo'
    else:
        name = 'results_by_model_all'

    if name not in plot_data:
        update_results_by_model(loo)

    models = plot_data[name]['model']
    f1_trace = []
    auc_trace = []
    prec_trace = []

    for i, model in enumerate(models):
        auc_trace.append(go.Scatter(
            x=plot_data[name]['dataset'][i],
            y=plot_data[name]['auc'][i],
            name=model,
            visible=True,
            mode='lines+markers'
        ))

        f1_trace.append(go.Scatter(
            y=plot_data[name]['f1'][i],
            x=plot_data[name]['dataset'][i],
            name=model,
            visible=False,
            mode='lines+markers'
        ))

        prec_trace.append(go.Scatter(
            y=plot_data[name]['avg_prec'][i],
            x=plot_data[name]['dataset'][i],
            name=model,
            visible=False,
            mode='lines+markers'
        ))

    auc_bools = [True] * len(models) + [False] * (2 * len(models))
    f1_bools = [False] * len(models) + [True] * len(models) + [False] * len(models)
    prec_bools = [False] * (2 * len(models)) + [True] * len(models)

    number_of_models = 0
    if plot_data[name]['auc']:
        number_of_models = len(plot_data[name]['auc'][0])

    layout = go.Layout(
        yaxis={'title': '<b>AUC</b>',
               'range': [0.5, 1],
               'tick0': 0.5,
               'dtick': 0.05,
               'ticklen': 10,
               'showgrid': True,
               },
        xaxis={'automargin': True,
               'title': '<b>Crank</b>',
               'dtick': 1,
               },
        title="<b>AUC scores for %d models</b>" % number_of_models,
        showlegend=True,
        updatemenus=list([
            dict(
                buttons=list([
                    dict(label='AUC',
                         method='update',
                         args=[{'visible': auc_bools},
                               {'title': "<b>AUC scores</b>",
                                'yaxis': {'title': '<b>AUC</b>',
                                          'range': [0.5, 1],
                                          'tick0': 0.5,
                                          'dtick': 0.05,
                                          'ticklen': 10,
                                          'showgrid': True,
                                          }},
                               ]),
                    dict(label='Avg. Prec',
                         method='update',
                         args=[{'visible': prec_bools},
                               {'title': "<b>Average Precision</b>",
                                'yaxis': {'title': '<b>Average Precision</b>',
                                          'range': [0, 1],
                                          'tick0': 0,
                                          'dtick': 0.1,
                                          'ticklen': 10,
                                          'showgrid': True,
                                          }},
                               ]),
                    dict(label='F1 Score',
                         method='update',
                         args=[{'visible': f1_bools},
                               {'title': "<b>F1 score</b>",
                                'yaxis': {'title': '<b>F1 Score</b>',
                                          'range': [0, 1],
                                          'tick0': 0,
                                          'dtick': 0.1,
                                          'ticklen': 10,
                                          'showgrid': True,
                                          }},
                               ]
                         ),
                ]),
                direction='right',
                showactive=True,
                type='buttons',
                y=1.4,
                yanchor='top'
            )
        ]),
    )
    graph = {'data': auc_trace + f1_trace + prec_trace, 'layout': layout}
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)

def filter_by_scores(rows):
    """Returns a dict of lists of experiments, where the position of the list corresponds to crystal score
        Args:
            rows (db.session.query) : database query result where each row represents an experiment
        Returns:
            dict of lists where the key is the crystal score
    """
    rows_by_scores = {}
    
    for i in range(1,5):
        rows_by_scores[i] = [exp for exp in rows if exp[2]==i]
    return rows_by_scores

def get_point_details(score, idx):
    """Returns experiment details based on what is clicked in the 3D plot

    Args:
        idx (int): Index of the point clicked on the plotly plot
    
    Returns:
        row corresponding to the index 

    """
    global plot_data
    name = 'scatter_3d_by_rxn'
    return plot_data[name]['data']['scores'][score+1][idx]

def update_scatter_3d_by_rxn(inchikey='all'):
    """Updates 3d scatter plot

    Args:
        inchikey (str) : inchikey of the organic amine to be shown on the plot. 'all' by default
    
    """
    name = 'scatter_3d_by_rxn'
    app.logger.info("Updating %s" % (name))
    plot_data[name]['xl'] = 0
    plot_data[name]['xu'] = 8
    plot_data[name]['intervals'] = [0.1, 0.25, 0.5, 0.75, 1]

    chemicals = {}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name

    if inchikey != 'all':
        rows = db.session.query(TrainingRun.name, TrainingRun.inchikey, TrainingRun._out_crystalscore, 
                                TrainingRun._rxn_M_organic, TrainingRun._rxn_M_inorganic, TrainingRun._rxn_M_acid).\
                                filter(TrainingRun.inchikey == inchikey).distinct().limit(10000).all()
    else:
        rows = db.session.query(TrainingRun.name, TrainingRun.inchikey, TrainingRun._out_crystalscore, 
                                TrainingRun._rxn_M_organic, TrainingRun._rxn_M_inorganic, TrainingRun._rxn_M_acid).\
                                distinct().limit(10000).all()
    
    inchis = set([x.inchikey for x in rows])
    rows_by_scores = filter_by_scores(rows)
    

    if len(inchis) == 1:
        out = chemicals[inchis.pop()]
    else:
        out = len(inchis)

    if inchikey == 'all':
        annotation = "<b>%d samples for %d chemicals</b>" % (len(rows), out)
    else:
        annotation = "<b>%d samples for %s</b>" % (len(rows), out)
    plot_data[name]['annotation'] = annotation

    app.logger.info(annotation)
    plot_data[name]['data'] = defaultdict(lambda: defaultdict(list))
    plot_data[name]['data']['scores'] = rows_by_scores
    


def scatter_3d_by_rxn():
    """Generates 3d scatter plot

    Returns:
        json object representing plotly figure

    """
    global plot_data
    name = 'scatter_3d_by_rxn'

    if name not in plot_data:
        update_scatter_3d_by_rxn()

    xl = plot_data[name]['xl']
    xu = plot_data[name]['xu']
    data = plot_data[name]['data']
    
    traces = []
    trace_colors = ['rgba(65, 118, 244, 1.0)', 'rgba(92, 244, 65, 1.0)',
                    'rgba(244, 238, 66, 1.0)', 'rgba(244, 66, 66, 1.0)']
    for score in plot_data[name]['data']['scores']:
        xdata = [exp[3] for exp in plot_data[name]['data']['scores'][score]]
        ydata = [exp[4] for exp in plot_data[name]['data']['scores'][score]]
        zdata = [exp[5] for exp in plot_data[name]['data']['scores'][score]]
        traces.append(go.Scatter3d(
                x=xdata,
                y=ydata,
                z=zdata,
                mode='markers',
                name='Score {}'.format(score),
                text=['<b>Inorganic</b>: {} <br><b>Organic</b>: {} <br><b>Acid</b>: {}'.format(xdata[i], ydata[i], zdata[i]) for i in range(len(xdata))],
                hoverinfo='text',
                marker=dict(
                    size=4,
                    color=trace_colors[score-1],
                    line=dict(
                        width=0.2
                    ),
                    opacity=1.0
                )
            ))

    buttons = []
    for i, interval in enumerate(plot_data[name]['intervals']):
        step = dict(
            label="%.2f resolution" % interval,
            method='update',
            args=[{'visible': [False] * len(traces)},
                  {'scene': {'xaxis': {'title': '<b>Inorganic Formula(M)</b>',
                                       'tickmode': 'linear',
                                       'tick0': xl,
                                       'dtick': interval,
                                       'range': [xl, xu],
                                       },
                             'yaxis': {'title': '<b>Organic Formula(M)</b>',
                                       'tickmode': 'linear',
                                       'tick0': xl,
                                       'dtick': interval,
                                       'range': [xl, xu],
                                       },
                             'zaxis': {'title': '<b>Acid Formula(M)</b>',
                                       'tickmode': 'linear',
                                       'tick0': xl,
                                       'dtick': interval,
                                       'range': [xl, xu],
                                       },
                             'aspectmode': 'manual',
                             'aspectratio': go.layout.scene.Aspectratio(
                                 x=1, y=1, z=1,
                             ),
                             }
                   },
                  ],
        )
        #step['args'][0]['visible'][i] = True  # Toggle i'th trace to "visible"
        buttons.append(step)

    layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        scene=dict(
            aspectmode='manual',
            aspectratio=go.layout.scene.Aspectratio(
                x=1, y=1, z=1,
            ),
            xaxis=dict(
                title='Inorganic Formula (M)',
                tickmode='linear',
                tick0=xl,
                dtick=0.5,
                range=[xl, xu],

            ),
            yaxis=dict(
                title='Organic Formula (M)',
                tickmode='linear',
                tick0=xl,
                dtick=0.5,
                range=[xl, xu],

            ),
            zaxis=dict(
                title='Acid Formula (M)',
                tickmode='linear',
                tick0=xl,
                dtick=0.5,
                range=[xl, xu],

            ),
        ),
        #showlegend=False,
        legend=go.layout.Legend(
                x=0,
                y=1,
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="black"
                ),
                bgcolor="LightSteelBlue",
                bordercolor="Black",
                borderwidth=2
            ),
        title=go.layout.Title(
            text=plot_data[name]['annotation'],
            xref='paper',
            x=0.5,
            y=0.95,
        ),
        width=1000,
        height=800,
    )

    graph = {'data': traces, 'layout': layout}
    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


def update_feature_importance():
    """Updates feature importance plots BBA and SHap

    """
    global plot_data
    name = 'feature_importance'

    names = {}
    features = get_features()
    for f in features:
        names[f.id] = f.name
    analyses = get_feature_analysis()

    plot_data['heldout'] = defaultdict(lambda: defaultdict(lambda: dict))
    plot_data['general'] = defaultdict(lambda: defaultdict(lambda: dict))

    for a in analyses:
        weight = defaultdict(list)
        rank = defaultdict(list)

        for r in a.rows:
            weight[names[r.feat_id]].append(r.weight)
            rank[names[r.feat_id]].append(r.rank)

        means = {}
        for feat in weight:
            means[feat] = np.mean(np.abs(weight[feat]))

        sorted_feats = [x[0] for x in sorted(means.items(), key=operator.itemgetter(1), reverse=True)]

        weight_out = []
        rank_out = []
        for f in sorted_feats[:10]:
            weight_out.append([f, weight[f]])
            rank_out.append([f, rank[f]])

        plot_data['heldout' if a.heldout_chem else 'general'][a.crank][a.method] = {
            'notes': a.notes,
            'weight': reversed(weight_out),
            'rank': reversed(rank_out),
        }


def feature_importance():
    """Generates feature importance plots
    Returns:
        json object representing plotly figure

    """
    global plot_data
    name = 'feature_importance'
    if name not in plot_data:
        update_feature_importance()

    # create one graph per feature_importance method
    graphs = {}

    heldout = plot_data['heldout']
    general = plot_data['general']
    cranks = sorted(heldout.keys(), reverse=True)
    if not cranks:
        # there is nothing in the db
        return {}

    crank = cranks[0]  # only plot the first crank
    method_types = heldout[crank].keys()  # heldout and general should be the same list

    for method in method_types:

        traces = []
        method_traces = {}

        method_traces[method + "-heldout"] = []
        method_traces[method + "-general"] = []

        for i, arr in enumerate(heldout[crank][method]['weight']):
            traces.append(go.Box(x=arr[1],
                                 name=arr[0].replace('_feat_', ''),
                                 visible=False,
                                 ))
            method_traces[method + "-heldout"].append(len(traces) - 1)  # assumes 1 crank!!

        for i, arr in enumerate(general[crank][method]['weight']):
            traces.append(go.Box(x=arr[1],
                                 name=arr[0].replace('_feat_', ''),
                                 visible=False,

                                 ))
            method_traces[method + "-general"].append(len(traces) - 1)  # assumes 1 crank!!

        buttons = []
        method_names = sorted(method_traces.keys())

        for m in method_names:
            if 'general' in m:
                title = "%s Features for Crank %s Across All Chemicals" % (method, crank)

            elif 'heldout' in m:
                title = "%s Features for Crank %s Heldout By Chemical" % (method, crank)
            else:
                title = "%s Features" % method

            b = dict(
                label=m,
                method='update',
                args=list([
                    dict(visible=[False] * len(traces)),
                    dict(
                        title=title,
                        xaxis=dict(
                            showgrid=False,
                            title="Feature Importance",
                            rangemode='nonnegative',
                            autorange=True
                        ),
                    ),
                ]),
            )

            for i in method_traces[m]:
                b['args'][0]['visible'][i] = True

            buttons.append(b)

            # initialize first method to true
            m = method_names[0]
            for i in method_traces[m]:
                traces[i]['visible'] = True

        layout = go.Layout(
            showlegend=False,
            title=buttons[0]['args'][1]['title'],
            yaxis=dict(
                automargin=True,
            ),

            xaxis=dict(
                showgrid=True,
                title="Feature Importance",
                rangemode='nonnegative',
                autorange=True
            ),
            height=600,
            updatemenus=list([
                dict(
                    buttons=buttons,
                    direction='down',
                    showactive=True,
                    active=0,
                    y=1.4,
                    yanchor='top'

                ),
            ]),
            hovermode=False,
        )

        graph = {'data': traces, 'layout': layout}
        graphs[method] = graph
    return json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)


