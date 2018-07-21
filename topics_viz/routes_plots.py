from topics_viz import app, db
from flask import render_template, url_for, redirect, request
from topics_viz.models import *
from bokeh.embed import components
import topics_viz.plots as plotter

@app.route("/ts<int:ts_id>/plots")
def plots(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis_list = db.session.query(TopicWordDistribution).filter(TopicWordDistribution.topicset_id == tset.id)

    return render_template('plots/plots_main.html', ts_id = tset.id, twdis_list = twdis_list)

@app.route("/plot/ts<int:ts_id>/plots_topics_nwords")
def plot_topics_nwords(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.topicid_nwords_vbar(ts_id)
    p2 = plotter.topics_nwords_histogram(ts_id)
    script, div = components((p, p2))
    return render_template('plots/plots_topics-nwords.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

@app.route("/plot/ts<int:ts_id>/plots_words_ntopics")
def plot_words_ntopics(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.wordid_ntopics_vbar(ts_id)
    p2 = plotter.words_ntopics_histogram(ts_id)
    script, div = components((p, p2))
    return render_template('plots/plots_words-ntopics.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

@app.route("/plot/ts<int:ts_id>/twdis<int:twdis_id>/summary")
def plot_twdis_summary(ts_id, twdis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one() # para que si no existe la twdis suceda un error

    p = plotter.twdis_summary(ts_id, twdis_id)
    script, div = components(p)
    return render_template('plots/plots_twdis_summary.html', ts_id = ts_id,
        twdis = twdis, script = script, div = div)

@app.route("/plot/ts<int:ts_id>/twdis<int:twdis_id>/topic<int:topic_id>")
def plot_twdis_topic(ts_id, twdis_id, topic_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error

    topic = db.session.query(Topic)\
        .filter(Topic.topicset_id == ts_id)\
        .filter(Topic.id == topic_id).one()

    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one() # para que si no existe la twdis suceda un error


    panorama, full = plotter.twdis_topic(ts_id, twdis_id, topic_id)
    script, div = components((panorama, full))
    return render_template('plots/plots_twdis_topic.html', ts_id = ts_id,
        twdis = twdis, topic = topic, script = script, div = div[0], div2 = div[1])

@app.route("/p")
def p():
    """
    Esto es solo para hacer pruebas ocasionales, mientras hago el desarrollo
    """
    return render_template('p.html', ts_id = 1)