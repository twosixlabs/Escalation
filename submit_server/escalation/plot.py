import plotly.graph_objs as go
import plotly
import json
import operator

from sqlalchemy import func
from collections import defaultdict
from flask import current_app as app
from sqlalchemy import text
from escalation import db
from .database import Submission, get_chemicals, get_leaderboard

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

    res=db.session.query(Submission.crank, func.count(Submission.crank)).group_by(Submission.crank).order_by(Submission.crank.asc()).all()

    plot_data['uploads_by_crank']['xs'] = [r[0] for r in res]
    plot_data['uploads_by_crank']['ys'] = [r[1] for r in res]
    app.logger.info("Updated plot 'uploads per crank'")

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

    print(plot_data[name])
    
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
    print(trace)
            
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
            mode='lines'
        ))
        
        f1_trace.append(go.Scatter(
            y = plot_data[name]['f1'][i],
            x = plot_data[name]['dataset'][i],            
            name=model,
            visible=False,
            mode='lines'            
        ))
        
        prec_trace.append(go.Scatter(
            y = plot_data[name]['avg_prec'][i],
            x = plot_data[name]['dataset'][i],
            name=model,
            visible=False,
            mode='lines'            
        ))
    print(auc_trace)
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
