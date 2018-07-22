from topics_viz import app, db
from flask import render_template, url_for, redirect, request
from topics_viz.models import *
from topics_viz.models_distributions import *
from bokeh.embed import components
import topics_viz.plots as plotter

@app.route("/ts<int:ts_id>/plot/plots_topics_nwords")
def plot_topics_nwords(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.topicid_nwords_vbar(ts_id)
    p2 = plotter.topics_nwords_histogram(ts_id)
    script, div = components((p, p2))
    return render_template('plots/plots_topics-nwords.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

@app.route("/ts<int:ts_id>/plot/plots_words_ntopics")
def plot_words_ntopics(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.wordid_ntopics_vbar(ts_id)
    p2 = plotter.words_ntopics_histogram(ts_id)
    script, div = components((p, p2))
    return render_template('plots/plots_words-ntopics.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

@app.route("/ts<int:ts_id>/distributions/twdis<int:twdis_id>/plot/summary")
def plot_twdis_summary(ts_id, twdis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one() # para que si no existe la twdis suceda un error

    p1, p2 = plotter.twdis_summary(ts_id, twdis_id)
    script, div = components((p1, p2))
    return render_template('plots/plots_twdis_summary.html', ts_id = ts_id,
        twdis = twdis, script = script, div = div[0], div2 = div[1])

@app.route("/ts<int:ts_id>/distributions/twdis<int:twdis_id>/plot/topic<int:topic_id>")
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

@app.route("/ts<int:ts_id>/distributions/tddis<int:tddis_id>/plot/summary")
def plot_tddis_summary(ts_id, tddis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one() # para que si no existe la twdis suceda un error

    p1, p2, p3 = plotter.tddis_summary(ts_id, tddis_id)
    script, div = components((p1, p2, p3))
    return render_template('plots/plots_tddis_summary.html', ts_id = ts_id,
        tddis = tddis, script = script, div1 = div[0], div2 = div[1], div3 = div[2])

@app.route("/ts<int:ts_id>/distributions/tddis<int:tddis_id>/plot/topic<int:topic_id>")
def plot_tddis_topic(ts_id, tddis_id, topic_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error

    topic = db.session.query(Topic)\
        .filter(Topic.topicset_id == ts_id)\
        .filter(Topic.id == topic_id).one()

    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one() # para que si no existe la tddis suceda un error


    panorama, full = plotter.tddis_topic(ts_id, tddis_id, topic_id)
    script, div = components((panorama, full))
    return render_template('plots/plots_tddis_topic.html', ts_id = ts_id,
        tddis = tddis, topic = topic, script = script, div = div[0], div2 = div[1])

@app.route("/p")
def p():
    """
    Esto es solo para hacer pruebas ocasionales, mientras hago el desarrollo
    """
    return render_template('p.html', ts_id = 1)
