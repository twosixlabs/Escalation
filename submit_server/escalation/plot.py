import plotly.graph_objs as go
import plotly
import json
import operator

from sqlalchemy import func
from collections import defaultdict
from flask import current_app as app
from sqlalchemy import text
from escalation import db
from .database import Submission, get_chemicals

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
        xaxis = {'title':"Ammonium Iodide Salt",
                 'automargin':True
        },
        yaxis = {'title':"Numbef of Experiments"},
        title = "Success Rate by Amine",
        )
    graph = {'data': [trace1, trace2],
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)
    
def update_uploads_per_crank():
    global plot_data

    res=db.session.query(Submission.crank, func.count(Submission.crank)).group_by(Submission.crank).order_by(Submission.crank.asc()).all()

    plot_data['uploads_per_crank']['xs'] = [r[0] for r in res]
    plot_data['uploads_per_crank']['ys'] = [r[1] for r in res]
    app.logger.info("Updated plot 'uploads per crank'")

def uploads_per_crank():
    global plot_data
    if 'uploads_per_crank' not in plot_data:
        update_uploads_per_crank()
            
    trace = go.Bar(
        x = plot_data['uploads_per_crank']['xs'],
        y = plot_data['uploads_per_crank']['ys']
    )

    layout = go.Layout(
        xaxis = { 'type' : 'category',
                  'title': "Crank",
        },
        yaxis = {'title': 'Number of Submissions'
        },
        title = "Number of Submissions per Crank"
        
    )
    graph = {'data': [trace],
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

def update_runs_per_crank():
    global plot_data    
    name = 'runs_per_crank'

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
    
def runs_per_crank():
    global plot_data
    name = 'runs_per_crank'

    if name not in plot_data:
        update_runs_per_crank()

    print(plot_data[name])        
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
        xaxis = {'title':"Progress By Weekly Crank",
                 'automargin':True,
                 'showgrid':False,
        },
        yaxis = {'title':"Number of Experiments",
                 'range': [0,1000 * (1 + max(plot_data[name]['ys_total']) // 1000)],
                 'showgrid':False,
        },
        title = "Total Number of Experiments over Time",
    )
    graph = {'data': [trace1, trace2],
             'layout': layout
    }
    return json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder)

