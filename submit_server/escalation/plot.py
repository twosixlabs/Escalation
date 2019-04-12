import plotly.graph_objs as go
import plotly
import json
import math
import operator
import os

from sqlalchemy import func
from collections import defaultdict
from flask import current_app as app
from sqlalchemy import text
from escalation import db
from .database import Submission, get_chemicals, get_leaderboard, get_perovskites_data
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
    
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
                                  {'title': "<b>Avgerage Precision over %d cranks</b>" % len(plot_data[name]['auc'][0]),
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
                                  {'title': "<b>Avgerage Precision</b>",
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
    app.logger.info("Updating %s" % (name))
    crank,csvfile=get_perovskites_data()
    csvfile =  os.path.join(app.config['UPLOAD_FOLDER'], csvfile)

    df = pd.read_csv(csvfile,comment='#')
    app.logger.info("Perovskites data length:%d" % (len(df)))

    feat_imp_cv = defaultdict(list)
    feat_imp_heldout = defaultdict(list)
    feats =  [x for x in df.columns if 'feat' in x] + ['_rxn_M_organic','_rxn_M_inorganic','_rxn_M_acid']

    for i in range(5):
        X_train, X_test,Y_train,Y_test = train_test_split(df[feats].values,[int(x) for x in df._out_crystalscore >= 4],test_size=0.2,random_state=i)
        clf = xgb.XGBClassifier(max_depth=3,feature_names=feats,objective='binary:logistic',eval_metric='auc',random_state=i)
        clf.fit(X_train, Y_train)

        for i, imp in enumerate(clf.feature_importances_):
            feat_imp_cv[feats[i]].append(imp)

    inchis=df['_rxn_organic-inchikey'].unique()
    for inchi in inchis:
        df1 = df[df['_rxn_organic-inchikey'] != inchi]
        df2 = df[df['_rxn_organic-inchikey'] == inchi]
        
        app.logger.info("%s: %d train, %d test" % (inchi, len(df1), len(df2)))
        X_train = df1[feats].values
        Y_train = [int(x) for x in df1._out_crystalscore >= 4]
        X_test = df2[feats].values
        Y_test = [int(x) for x in df2._out_crystalscore >= 4]
        clf = xgb.XGBClassifier(max_depth=3,feature_names=feats,objective='binary:logistic',eval_metric='auc')
        clf.fit(X_train, Y_train)
        for i, imp in enumerate(clf.feature_importances_):
            feat_imp_heldout[feats[i]].append(imp)

           
    plot_data[name]['heldout'] = feat_imp_heldout
    plot_data[name]['cv']      = feat_imp_cv
    plot_data[name]['feats']   = feats
    plot_data[name]['inchis']  = inchis
    plot_data[name]['crank']   = crank


def feature_importance():
    global plot_data
    name = 'feature_importance'
    if name not in plot_data:
        update_feature_importance()
    feats   = plot_data[name]['feats']
    cv      = plot_data[name]['cv']
    heldout = plot_data[name]['heldout']
    inchis  = plot_data[name]['inchis']
    crank   = plot_data[name]['crank']
    mean={}
    
    for i, feat in enumerate(feats):
        mean[feat] = sum(cv[feat])/len(cv[feat])

    cv_bools = []
    general_bools = []
    sorted_feats = [x[0] for x in sorted(mean.items(),key=operator.itemgetter(1),reverse=True)]

    traces=[]
    for i, feat in enumerate(sorted_feats[:10]):
        traces.append(go.Box(x=cv[feat],
                             name=feat.replace('_feat_',''),
                             visible=True,
        )
        )
        general_bools.append(True)
        cv_bools.append(False)
        traces.append(go.Box(x=heldout[feat],
                             name=feat.replace('_feat_',''),
                             visible=False,
        )
        )
        general_bools.append(False)
        cv_bools.append(True)
        

    layout = go.Layout(
        showlegend=False,
        title="Top 10 features by importance for %d chemicals with crank %s" % (len(inchis),crank),
        updatemenus=list([
            dict(
                buttons=list([
                    dict(label = 'All Chemicals',
                         method = 'update',
                         args = [{'visible': general_bools},
                         ]),
                    dict(label = 'Heldout by Chemical',
                         method = 'update',
                         args = [{'visible': cv_bools},
                         ]),
                    ]),
                    x = -0.5,
                    xanchor = 'left',
                    y = 1.1,
                    yanchor = 'top'                 

            )
        ]),
        yaxis=dict(
        ),

        xaxis=dict(
            showgrid=True,            
            title="Feature Importance",            
        ),
        height=600
    )
    
    graph  = {'data':traces, 'layout': layout}
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)


