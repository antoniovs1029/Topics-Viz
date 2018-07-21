from topics_viz import app, db
from flask import render_template, url_for, redirect, request
from topics_viz.models import *
from bokeh.embed import components
import topics_viz.plots as plotter

@app.route("/ts<int:ts_id>/plots")
def plots(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    return render_template('plots/plots_main.html', ts_id = tset.id)

@app.route("/ts<int:ts_id>/plots_topics_nwords")
def plot_topics_nwords(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.topicid_nwords_vbar(ts_id)
    p2 = plotter.topics_nwords_histogram(ts_id)
    script, div = components((p, p2))
    print(div)
    return render_template('plots/plots_topics-nwords.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

@app.route("/p")
def p():
    """
    Esto es solo para hacer pruebas ocasionales, mientras hago el desarrollo
    """
    return render_template('p.html', ts_id = 1)
