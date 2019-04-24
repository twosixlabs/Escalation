import plotly.graph_objs as go
import plotly
import json
import math
import operator
import os

from sqlalchemy import func
from collections import defaultdict, Counter
from flask import current_app as app
from sqlalchemy import text
from escalation import db
from .database import Submission, get_chemicals, get_leaderboard, get_perovskites_data, get_feature_analysis, get_features, get_training, RepoStat, TrainingRun

import numpy as np
import pandas as pd
global plot_data

plot_data = defaultdict(dict)

def update_success_by_amine():
    global plot_data
    name='sucess_by_amine'

    chemicals={}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name
    
    sql = text('select distinct name,inchikey,_out_crystalscore,_rxn_M_organic,_rxn_M_inorganic,_rxn_M_acid from training_run')
    rows = list(db.engine.execute(sql))
    
    #0 name
    #1 inchikey
    #2 _out_crystalscore
    #3 _rxn_M_organic
    #4 _rxn_M_inorganic
    #5 _rxn_M_acid
    
    total = defaultdict(int)
    success = defaultdict(int)
    for r in rows:
        total[r[1]] += 1
        if r[2] == 4:
            success[r[1]] += 1

    sorted_amine = [x[0] for x in sorted(total.items(), key=operator.itemgetter(1)) ]
    plot_data[name]['xs'] = [chemicals[amine] if amine in chemicals else amine for amine in sorted_amine ]
    plot_data[name]['ys_success'] = [ success[amine] for amine in sorted_amine]
    plot_data[name]['ys_total'] = [total[amine] for amine in sorted_amine]
    
def success_by_amine():
    global plot_data
    name='sucess_by_amine'
            
    if name not in plot_data:
        update_success_by_amine()

    trace1 = go.Bar(
        x = plot_data[name]['xs'],
        y = plot_data[name]['ys_success'],
        name = "Successes",
        marker = {
            'color':'#5eabdb'
            }
    )
    trace2 = go.Bar(
        x = plot_data[name]['xs'],
        y = plot_data[name]['ys_total'],
        name = "Total",
        marker = {
            'color':'#a55942'
            }
    )
    layout = go.Layout(
        xaxis = {'title':"<b>Ammonium Iodide Salt</b>",
                 'automargin':True
        },
        yaxis = {'title':"<b>Numbef of Experiments</b>"},
        title = "<b>Success Rate by Amine</b>",
        )
    graph = {'data': [trace1, trace2],
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)
    
def update_uploads_by_crank():
    global plot_data
    app.logger.info("Updating uploads_by_crank")
    res=db.session.query(Submission.crank, func.count(Submission.crank)).group_by(Submission.crank).order_by(Submission.crank.asc()).all()

    plot_data['uploads_by_crank']['xs'] = [r[0] for r in res]
    plot_data['uploads_by_crank']['ys'] = [r[1] for r in res]

def uploads_by_crank():
    global plot_data
    if 'uploads_by_crank' not in plot_data:
        update_uploads_by_crank()

        
            
    trace = go.Bar(
        x = plot_data['uploads_by_crank']['xs'],
        y = plot_data['uploads_by_crank']['ys']
    )

    layout = go.Layout(
        xaxis = { 'type' : 'category',
                  'title': "<b>Crank</b>",
        },
        yaxis = {'title': '<b>Number of Submissions</b>'
        },
        title = "<b>Number of Submissions per Crank</b>"
        
    )
    graph = {'data': [trace],
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

def update_runs_by_crank():
    global plot_data    
    name = 'runs_by_crank'
    app.logger.info("Updating %s" % (name))
    total = defaultdict(int)
    success = defaultdict(int)
    
    sql = text('select count(_out_crystalscore), dataset from training_run group by dataset')
    rows = list(db.engine.execute(sql))
    for row in rows:
        total[row[1]] = row[0]

    sql = text('select count(_out_crystalscore), dataset from training_run where _out_crystalscore = 4 group by dataset')
    rows = list(db.engine.execute(sql))
    for row in rows:
        success[row[1]] = row[0]
        

    sorted_list = sorted(total.keys())#[x[0] for x in sorted(total.items(), key=operator.itemgetter(1)) ]
    plot_data[name]['xs'] = [crank for crank in sorted_list ]
    plot_data[name]['ys_success'] = [ success[crank] for crank in sorted_list]
    plot_data[name]['ys_total'] = [total[crank] for crank in sorted_list]
    
def runs_by_crank():
    global plot_data
    name = 'runs_by_crank'

    if name not in plot_data:
        update_runs_by_crank()

    trace1 = go.Scatter(
        x = plot_data[name]['xs'],
        y = plot_data[name]['ys_total'],
        mode = 'lines',
        name = "Total",
        marker = {
            'color':'#a55942',
        }
    )
    trace2 = go.Scatter(
        x = plot_data[name]['xs'],
        y = plot_data[name]['ys_success'],
        mode = 'lines',        
        name = "Successes",
        marker = {
            'color':'#5eabdb',
            }
    )    
    layout = go.Layout(
        xaxis = {'title':"<b>Progress By Weekly Crank</b>",
                 'automargin':True,
                 'showgrid':False,
        },
        yaxis = {'title':"<b>Number of Experiments</b>",
                 'range': [0,1000 * (1 + max(plot_data[name]['ys_total']) // 1000)],
                 'showgrid':False,
        },
        title = "<b>Total Number of Experiments over Time</b>",
    )
    graph = {'data': [trace1, trace2],
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)


def update_runs_by_month():
    global plot_data    
    name = 'runs_by_month'
    app.logger.info("Updating %s" % (name))
    if name not in plot_data:
        update_runs_by_crank()

    total = defaultdict(int)
    success = defaultdict(int)
    
    sql = text('select distinct name,inchikey from training_run')
    rows = list(db.engine.execute(sql))

    xs = set()
    by_inchi = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    for row in rows:
        by_inchi[row[1]][row[0][:7]] += 1
        xs.add(row[0][:7])
        totals[row[1]] += 1

    xs = sorted(list(xs))
    ys_dict = {}
    monthy = defaultdict(int)
    sorted_inchis = [x[0] for x in sorted(totals.items(),key=operator.itemgetter(1),reverse=True)]
    for inchi in sorted_inchis:
        ys = []

        for month in xs:
            ys.append(by_inchi[inchi][month])
            monthy[month] += by_inchi[inchi][month]
        ys_dict[inchi] = ys

    max_y = 0
    for month,y in monthy.items():
        if y > max_y:
            max_y = y
            
    plot_data[name]['xs'] = xs
    plot_data[name]['ys'] = ys_dict
    plot_data[name]['ymax'] = max_y
    
def runs_by_month():
    global plot_data
    name = 'runs_by_month'

    chemicals={}
    abbrev={}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name
        abbrev[r.inchi] = r.abbrev
    
    if name not in plot_data:
        update_runs_by_month()

    trace = []
    for inchi,ys in plot_data[name]['ys'].items():
        chem = chemicals[inchi] if inchi in chemicals else inchi
        abb = abbrev[inchi] if inchi in chemicals else inchi[:7]
        trace.append(go.Bar(
            x = plot_data[name]['xs'],
            y = ys,
            text = ["%d %s" % (y, abb ) for y in ys],
            name = chem,
            hoverlabel = dict(namelength = -1),
            hoverinfo = 'text',
            marker={'color':[ '#5eabdb' for x in plot_data[name]['xs']],
                    'line': {'color':'#000000', 'width':1},
            }
        ))

        
    layout = go.Layout(
        xaxis = {'title':"<b>Progress By Month</b>",
                 'automargin':True,
                 'showgrid':False,
                 'tickangle':45,
        },
        yaxis = {'title':"<b>Number of Experiments</b>",
                 'range': [0,100 * (1 + plot_data[name]['ymax'] // 100)],
                 'showgrid':False,
        },
        title = "<b>Number of Experiments per Month</b>",
        barmode='stack',
        hovermode='closest',
        showlegend=False,
    )
    graph = {'data': trace,
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)


def update_results_by_model():
    name = 'results_by_model'
    app.logger.info("Updating %s" % (name))    
    global plot_data

    res = get_leaderboard()
    results = defaultdict(list)

    # first group the data together by model
    for r in res:
        results[r.model_name].append(r)

    #sort array of rows by their dataset name
    for m in results:
        results[m] = sorted(results[m], key=lambda x: x.dataset_name)
        
    d_f1= defaultdict(list)
    d_auc= defaultdict(list)
    d_avg_prec= defaultdict(list)    
    d_prec= defaultdict(list)
    d_rec= defaultdict(list)
    d_dataset= defaultdict(list)

    #now we hav a sorted dict of numbers by model
    for m in results:
        d_f1[m]       = [x.f1_score for x in results[m]]
        d_auc[m]      = [x.auc_score for x in results[m]]
        d_avg_prec[m] = [x.average_precision for x in results[m]]
        d_rec[m]      = [x.recall for x in results[m]]
        d_prec[m]     = [x.precision for x in results[m]]
        d_dataset[m]  = [x.dataset_name for x in results[m]]                

    plot_data[name]['f1']       = []
    plot_data[name]['auc']      = []
    plot_data[name]['avg_prec'] = []    
    plot_data[name]['model']    = []
    plot_data[name]['prec']     = []
    plot_data[name]['rec']      = []
    plot_data[name]['dataset']  = []    


    #sort models by their means
    means = defaultdict(float)
    for model,arr in d_auc.items():
        means[model] = sum(arr)/len(arr)
    sorted_models = [x[0] for x in sorted(means.items(),key=operator.itemgetter(1),reverse=False)]

    for model in sorted_models:
        plot_data[name]['model'].append(model)
        plot_data[name]['f1'].append(d_f1[model])
        plot_data[name]['auc'].append(d_auc[model])
        plot_data[name]['rec'].append(d_rec[model])
        plot_data[name]['prec'].append(d_prec[model])        
        plot_data[name]['avg_prec'].append(d_avg_prec[model])        
        plot_data[name]['dataset'].append(d_dataset[model])                

def results_by_model():
    name = 'results_by_model'
    global plot_data

    if name not in plot_data:
        update_results_by_model()

    models = plot_data[name]['model']
    f1_trace=[]
    auc_trace=[]
    prec_trace=[]    
    for i,model in enumerate(models):

        auc_trace.append(go.Box(
            x = plot_data[name]['auc'][i],
            name=model,
            visible=True,
        ))
        
        f1_trace.append(go.Box(
            x = plot_data[name]['f1'][i],
            name=model,
            visible=False,
        ))
        
        prec_trace.append(go.Box(
            x = plot_data[name]['avg_prec'][i],
            name=model,
            visible=False,
        ))        
    auc_bools = [True] * len(models) + [False] * (2 * len(models))
    f1_bools = [False] * len(models) + [True] * len(models) + [False] * len(models)
    prec_bools = [False] * (2 * len(models)) + [True] * len(models)
    layout = go.Layout(
        xaxis = {'title': '<b>AUC</b>',
                 'range':[0.5,1],
                 'tick0':0.5,
                 'dtick':0.05,
                 'ticklen':10,
                 'showgrid':True,                 
        },
        yaxis = {'automargin':True,
                 'title':'<b>Classifier</b>',
        },
        title = "<b>AUC scores over %d cranks</b>" % len(plot_data[name]['auc'][0]),          
        showlegend=False,
        updatemenus=list([
            dict(
                 buttons=list([   
                     dict(label = 'AUC',
                          method = 'update',
                          args = [{'visible': auc_bools},
                                  {'title': "<b>AUC scores over %d cranks</b>" % len(plot_data[name]['auc'][0]),
                                   'xaxis':{'title':'<b>AUC</b>',
                                            'range':[0.5,1],
                                            'tick0':0.5,
                                            'dtick':0.05,
                                            'ticklen':10,
                                            'showgrid':True,                                            
                                   }},
                          ]),
                     dict(label = 'Avg. Prec',
                          method = 'update',
                          args = [{'visible': prec_bools},
                                  {'title': "<b>Average Precision over %d cranks</b>" % len(plot_data[name]['auc'][0]),
                                   'xaxis':{'title':'<b>Average Precision</b>',
                                            'range':[0,1],
                                            'tick0':0,
                                            'dtick':0.1,
                                            'ticklen':10,
                                            'showgrid':True,                                            
                                   }},
                          ]),
                     dict(label = 'F1 Score',
                          method = 'update',
                          args = [{'visible': f1_bools},
                                  {'title': "<b>F1 scores over %d cranks</b>" % len(plot_data[name]['auc'][0]),
                                   'xaxis':{'title':'<b>F1 Score</b>',
                                            'range':[0,1],
                                            'tick0':0,
                                            'dtick':0.1,
                                            'ticklen':10,
                                            'showgrid':True,
                                   }},
                          ]
                     ),
                     ]),
                direction = 'right',
                showactive = True,
                type = 'buttons',
                y = 1.4,
                yanchor = 'top' 
        )
        ]),
    )
    graph  = {'data':auc_trace+f1_trace+prec_trace, 'layout': layout}
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

def f1_by_model():
    global plot_data
    name = 'results_by_model'

    #uses the same update function as above
    if name not in plot_data:
        update_results_by_model()

    models = plot_data[name]['model']
    colors= [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
    ]

    trace=[]
    shapes=[]
    for i,model in enumerate(models):
        trace.append(go.Scatter(
            x = plot_data[name]['prec'][i],
            y = plot_data[name]['rec'][i],
            text = plot_data[name]['dataset'][i],
            name=model,
            mode='markers',
            marker= dict(size=12,
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
        width = 1000,
        height = 600,
        xaxis = {'title': '<b>Precision</b>',
                 'range':[0,1],
                 'tick0':0,
                 'dtick':0.1,
                 'ticklen':10,
                 'showgrid':True,                 
        },
        yaxis = {
            'title':'<b>Recall</b>',
            'range':[0,1],
            'tick0':0,
            'dtick':0.1,
            'ticklen':10,
            'showgrid':True,                             
        },
        title = "<b>Precision and Recall</b>",
        showlegend=True,
#        shapes=shapes,
    )
            
    graph  = {'data':trace, 'layout': layout}
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

    
def results_by_crank():
    global plot_data
    name = 'results_by_model'

    if name not in plot_data:
        update_results_by_model()
        
    models = plot_data[name]['model']
    f1_trace=[]
    auc_trace=[]
    prec_trace=[]
    
    for i,model in enumerate(models):
        auc_trace.append(go.Scatter(
            x = plot_data[name]['dataset'][i],
            y = plot_data[name]['auc'][i],            
            name=model,
            visible=True,
            mode='lines+markers'
        ))
        
        f1_trace.append(go.Scatter(
            y = plot_data[name]['f1'][i],
            x = plot_data[name]['dataset'][i],            
            name=model,
            visible=False,
            mode='lines+markers'            
        ))
        
        prec_trace.append(go.Scatter(
            y = plot_data[name]['avg_prec'][i],
            x = plot_data[name]['dataset'][i],
            name=model,
            visible=False,
            mode='lines+markers'            
        ))
        
    auc_bools = [True] * len(models) + [False] * (2 * len(models))
    f1_bools = [False] * len(models) + [True] * len(models) + [False] * len(models)
    prec_bools = [False] * (2 * len(models)) + [True] * len(models)
    layout = go.Layout(
        yaxis = {'title': '<b>AUC</b>',
                 'range':[0.5,1],
                 'tick0':0.5,
                 'dtick':0.05,
                 'ticklen':10,
                 'showgrid':True,                 
        },
        xaxis = {'automargin':True,
                 'title':'<b>Crank</b>',
                 'dtick':1,
        },
        title = "<b>AUC scores for %d models</b>" % len(plot_data[name]['auc'][0]),          
        showlegend=True,
        updatemenus=list([
            dict(
                 buttons=list([   
                     dict(label = 'AUC',
                          method = 'update',
                          args = [{'visible': auc_bools},
                                  {'title': "<b>AUC scores</b>",
                                   'yaxis':{'title':'<b>AUC</b>',
                                            'range':[0.5,1],
                                            'tick0':0.5,
                                            'dtick':0.05,
                                            'ticklen':10,
                                            'showgrid':True,                                            
                                   }},
                          ]),
                     dict(label = 'Avg. Prec',
                          method = 'update',
                          args = [{'visible': prec_bools},
                                  {'title': "<b>Average Precision</b>",
                                   'yaxis':{'title':'<b>Average Precision</b>',
                                            'range':[0,1],
                                            'tick0':0,
                                            'dtick':0.1,
                                            'ticklen':10,
                                            'showgrid':True,                                            
                                   }},
                          ]),
                     dict(label = 'F1 Score',
                          method = 'update',
                          args = [{'visible': f1_bools},
                                  {'title': "<b>F1 score</b>",
                                   'yaxis':{'title':'<b>F1 Score</b>',
                                            'range':[0,1],
                                            'tick0':0,
                                            'dtick':0.1,
                                            'ticklen':10,
                                            'showgrid':True,
                                   }},
                          ]
                     ),
                     ]),
                direction = 'right',
                showactive = True,
                type = 'buttons',
                y = 1.4,
                yanchor = 'top' 
        )
        ]),
    )
    graph  = {'data':auc_trace+f1_trace+prec_trace, 'layout': layout}
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

def cluster(interval=0.1,xmin=0,xmax=4,X=[]):
    dz = dy = dx = interval
    xl = yl = zl = xmin
    xu = yu = zu = xmax
    s = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    n = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for x in X:
        s[x._rxn_M_organic//dx][x._rxn_M_inorganic//dy][x._rxn_M_acid//dz] += x._out_crystalscore
        n[x._rxn_M_organic//dx][x._rxn_M_inorganic//dy][x._rxn_M_acid//dz] += 1
    xs=[]
    ys=[]
    zs=[]
    ss=[]
    ns=[]

    for x in sorted(s.keys()):
        for y in sorted(s[x].keys()):
            for z in sorted(s[x][y].keys()):
                xs.append(dx*x + dx/2)
                ys.append(dy*y + dy/2)
                zs.append(dz*z + dz/2)
                ss.append(s[x][y][z]/n[x][y][z])
                ns.append(n[x][y][z])
    m = max(ns)
    sizes = [2+10*(0.4244 * x**(1/3)) for x in ns]
    texts=["%d,%.2f" % x for x in zip(ns,ss)]
    
    return xs, ys, zs, ss, ns, sizes, texts

def update_scatter_3d_by_rxn(inchikey='all'):
    name = 'scatter_3d_by_rxn'
    app.logger.info("Updating %s" % (name))    
    plot_data[name]['xl'] = 0
    plot_data[name]['xu'] = 8
    plot_data[name]['intervals']=[0.1,0.25,0.5,0.75,1]
    
    chemicals={}
    res = get_chemicals()
    for r in res:
        chemicals[r.inchi] = r.common_name

    if inchikey != 'all':
        sql = text('select distinct name,inchikey,_out_crystalscore,_rxn_M_organic,_rxn_M_inorganic,_rxn_M_acid from training_run where inchikey = "%s" limit 10000' % inchikey)
    else:
        sql = text('select distinct name,inchikey,_out_crystalscore,_rxn_M_organic,_rxn_M_inorganic,_rxn_M_acid from training_run limit 10000')
        
    rows = list(db.engine.execute(sql))
    inchis = set([x.inchikey for x in rows])
    
    if len(inchis) == 1:
        out = chemicals[inchis.pop()]
    else:
        out = len(inchis)

    if inchikey == 'all':
        annotation = "<b>%d samples for %d chemicals</b>" % (len(rows),out)
    else:
        annotation = "<b>%d samples for %s</b>" % (len(rows),out)
    plot_data[name]['annotation'] = annotation
    
    app.logger.info(annotation)
    plot_data[name]['data'] = defaultdict(lambda: defaultdict(list))
    for interval in plot_data[name]['intervals']:
        xs, ys, zs, ss, ns, size, texts = cluster(interval,plot_data[name]['xl'],plot_data[name]['xu'],rows)
        plot_data[name]['data'][interval]['xs'] = xs
        plot_data[name]['data'][interval]['ys'] = ys
        plot_data[name]['data'][interval]['zs'] = zs
        plot_data[name]['data'][interval]['ss'] = ss
        plot_data[name]['data'][interval]['ns'] = ns
        plot_data[name]['data'][interval]['size'] = size
        plot_data[name]['data'][interval]['text'] = texts
    
                    
def scatter_3d_by_rxn():
    global plot_data
    name = 'scatter_3d_by_rxn'

    if name not in plot_data:
        update_scatter_3d_by_rxn()

    xl = plot_data[name]['xl']
    xu = plot_data[name]['xu']    
    data = plot_data[name]['data']
    traces=[]
    for interval in plot_data[name]['intervals']:
        traces.append(go.Scatter3d(
            x = data[interval]['xs'],
            y = data[interval]['ys'],
            z = data[interval]['zs'],
            mode = 'markers',
            hoverlabel = dict(namelength = -1),
            hoverinfo = 'text',
            text = data[interval]['text'],
            marker = dict(opacity = 0.7,
                          color=data[interval]['ss'],
                          size=data[interval]['size'],
                          colorscale='Portland',
                          colorbar=dict(title='Crystal Score',
                                        tick0=0,
                                        dtick=1,
                          ),
                          cmax=4,
                          cmin=1
                          ),
            visible=False
            ))
    traces[2]['visible']=True

    buttons=[]
    for i, interval in enumerate(plot_data[name]['intervals']):
        step = dict(
            label = "%.2f resolution" % interval,
            method = 'update',  
            args = [{'visible': [False] * len(traces)},
                    { 'scene':{'xaxis':{'title':'<b>Inorganic Formula(M)</b>',
                                        'tickmode':'linear',
                                        'tick0':xl,
                                        'dtick':interval,
                                        'range':[xl,xu],
                    },
                               'yaxis':{'title':'<b>Organic Formula(M)</b>',
                                        'tickmode':'linear',
                                        'tick0':xl,
                                        'dtick':interval,
                                        'range':[xl,xu],
                               },
                               'zaxis':{'title':'<b>Acid Formula(M)</b>',
                                        'tickmode':'linear',
                                        'tick0':xl,
                                        'dtick':interval,
                                        'range':[xl,xu],
                               },
                               'aspectmode':'manual',
                               'aspectratio':go.layout.scene.Aspectratio(
                                   x=1, y=1, z=1,
                               )  ,      
                    }
                    },
            ] ,
        )
        step['args'][0]['visible'][i] = True # Toggle i'th trace to "visible"
        buttons.append(step)

    layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        scene = dict(
            aspectmode='manual',
            aspectratio=go.layout.scene.Aspectratio(
                x=1, y=1, z=1,
            )  ,      
            xaxis = dict(
                title='Inorganic Formula (M)',
                tickmode='linear',
                tick0=xl,
                dtick=0.5,
                range=[xl,xu],

            ),
            yaxis = dict(
                title='Organic Formula (M)',
                tickmode='linear',
                tick0=xl,
                dtick=0.5,
                range=[xl,xu],

            ),
            zaxis = dict(
                title='Acid Formula (M)',
                tickmode='linear',
                tick0=xl,
                dtick=0.5,
                range=[xl,xu],

            ),
        ),
        updatemenus=list([
            dict(
                buttons=buttons,
                
                direction = 'down',
                showactive = True,
                type = 'buttons',
                active=2
            )]),
        showlegend=False,
        title=go.layout.Title(
            text=plot_data[name]['annotation'],
            xref='paper',
            x=0.5,
            y=0.95,
    ),
        width=1000,
        height=800,
        )

    
    graph  = {'data':traces, 'layout': layout}
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

def update_feature_importance():
    global plot_data
    name = 'feature_importance'

    names={}
    features = get_features()
    for f in features:
        names[f.id] = f.name
    analyses = get_feature_analysis()
    
    plot_data['heldout'] = defaultdict(lambda: defaultdict(lambda: dict))
    plot_data['general'] = defaultdict(lambda: defaultdict(lambda: dict))
    
    for a in analyses:
        weight=defaultdict(list)
        rank=defaultdict(list)

        for r in a.rows:
            weight[names[r.feat_id]].append(r.weight)
            rank[names[r.feat_id]].append(r.rank)

        means={}
        for feat in weight:
            means[feat] = np.mean(np.abs(weight[feat]))
            
        sorted_feats = [x[0] for x in sorted(means.items(),key=operator.itemgetter(1),reverse=True)]

        weight_out=[]
        rank_out=[]
        for f in sorted_feats[:10]:
            weight_out.append([f,weight[f]])
            rank_out.append([f,rank[f]])            

        plot_data['heldout' if a.heldout_chem else 'general'][a.crank][a.method] = {
            'notes'  : a.notes,            
            'weight' : reversed(weight_out),
            'rank'   : reversed(rank_out),
        }
            
def feature_importance():
    global plot_data
    name = 'feature_importance'
    if name not in plot_data:
        update_feature_importance()
        
    heldout = plot_data['heldout']
    general = plot_data['general']

    traces=[]
    method_traces={}

    cranks = sorted(heldout.keys(),reverse=True)
    crank = cranks[0] #only plot the first crank
    
    for method in heldout[crank]:
        
        method_traces[method+"-heldout"] = []
        method_traces[method+"-general"] = []        

        for i, arr in enumerate(heldout[crank][method]['weight']):
            traces.append(go.Box(x=arr[1],
                                 name=arr[0].replace('_feat_',''),
                                 visible=False,
            ))
            method_traces[method+"-heldout"].append(len(traces)-1) #assumes 1 crank!!

        for i, arr in enumerate(general[crank][method]['weight']):
            traces.append(go.Box(x=arr[1],
                                 name=arr[0].replace('_feat_',''),
                                 visible=False,
                                 
                                 
            ))
            method_traces[method+"-general"].append(len(traces)-1) #assumes 1 crank!!            

    buttons=[]
    method_names = sorted(method_traces.keys())
    
    for m in method_names:
        if 'general' in m:
            title="Important Features for Crank %s Across All Chemicals" % crank
            
        elif 'heldout' in m:
            title="Important Features for Crank %s Heldout By Chemical" % crank
        else:
            title="Feature Importances"
                
        b = dict(
            label = m,
            method='update',
            args = list([
                dict(visible=[False] * len(traces) ),
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

        #initialize first method to true
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
                y = 1.4,
                yanchor = 'top' 
                
                ),
        ]),
        hovermode=False,
    )
    
    graph  = {'data':traces, 'layout': layout}
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

def repo_cluster(df, prec):
    features = ['_rxn_M_inorganic','_rxn_M_organic','_rxn_M_acid', '_rxn_temperatureC_actual_bulk', '_out_crystalscore', 'inchikey']
    vals = df[features].values
    temp_prec = 3
    clusters = []
    memo = {}
    for i, v in enumerate(vals):
        if i in memo:
            continue
        cluster = [i]
        for j, v_ in enumerate(vals):
            if j in memo:
                continue
            if i == j:
                continue
            if abs(v[3] - v_[3]) > temp_prec:
                continue
            if not any(abs(v[:3] - v_[:3]) > prec): #these are different
                cluster.append(j)
        if len(cluster) != 1:
            for z in cluster:
                memo[z] = 0
            clusters.append(vals[cluster])

    data = []
    for i,k in enumerate(clusters):
        data.append({})
        cs = k[:,4]
        data[i]['cs'] = round(np.mean(cs,axis=0),2)
        data[i]['size'] = len(cs)
        data[i]['inorganic'] = round(np.mean(k[:,0],axis=0),2)
        data[i]['organic']   = round(np.mean(k[:,1],axis=0),2)
        data[i]['acid']      = round(np.mean(k[:,2],axis=0),2)
        data[i]['temp']      = round(np.mean(k[:,3],axis=0),2)
        cntr = Counter(cs)
        lbl = cntr.most_common(1)[0][0]
        data[i]['purity'] = round(cntr[lbl] / len(cs),2)
    return data

def update_repo_table(prec=0.25,inchi='all'):
    global plot_data
    name = 'exp_repo'    
    #update reproducibility
    RepoStat.query.delete()

    query="select * from training_run where dataset in (select max(dataset) dataset from training_run as m)"
    df = pd.read_sql(query ,db.session.bind)
    app.logger.info("Selected %d training runs" % len(df))
    if inchi != 'all':
        df = df[df.inchikey == inchi]
        app.logger.info("Filtered to %d runs for inchi %s" % (len(df), inchi))

    
    data = repo_cluster(df, prec)
    objs=[]
    mean_cs = 0
    mean_purity = 0
    for row in data:
        objs.append(RepoStat(inorganic=row['inorganic'],
                             organic=row['organic'],
                             acid=row['acid'],
                             temp=row['temp'],
                             size=row['size'],
                             score=row['cs'],
                             repo=round(row['purity'],2)
        ))
        mean_cs += row['cs']
        mean_purity += row['purity']

    mean_cs /= len(data)
    mean_purity /= len(data)
    
    app.logger.info("Added %d clusters" % len(objs))

    db.session.bulk_save_objects(objs)
    db.session.commit()

    plot_data[name] = {}
    plot_data[name]['inchi']  = inchi
    plot_data[name]['prec']   = prec
    plot_data[name]['size']   = len(data)
    plot_data[name]['score']  = round(mean_cs,2)
    plot_data[name]['purity'] = round(mean_purity,2)
    plot_data[name]['expts']  = len(df)
    
def repo_table_stats():
    global plot_data
    name = 'exp_repo'
    return plot_data[name]
    
