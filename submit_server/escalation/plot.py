import plotly.graph_objs as go
import plotly
import json
from sqlalchemy import func
from collections import defaultdict
from flask import current_app as app

from escalation import db
from .database import Submission

global plot_data

plot_data = defaultdict(dict)
def update_uploads_per_crank():
    global plot_data

    res=db.session.query(Submission.crank, func.count(Submission.crank)).group_by(Submission.crank).order_by(Submission.crank.asc()).all()
    import random
    v = random.randint(0,10)
    res.append(('foo',v))
    plot_data['uploads_per_crank']['xs'] = [r[0] for r in res]
    plot_data['uploads_per_crank']['ys'] = [r[1] for r in res]
    app.logger.info("Updated plot 'uploads per crank'")

def uploads_per_crank():
    global plot_data
    if 'uploads_per_crank' not in plot_data:
        print("pushing update for uploads")
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
    
