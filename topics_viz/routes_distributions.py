from topics_viz import app, db
from flask import render_template, url_for, redirect, request, Response
from topics_viz.models import *
from topics_viz.models_distributions import *
from topics_viz.templates_python import create_HTML_table

#### Menú principal de distribuciones
@app.route("/ts<int:ts_id>/distributions")
def distributions(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis_list = TopicWordDistribution.query.filter_by(topicset_id = tset.id).all()
    tddis_list = TopicDocumentDistribution.query.filter_by(topicset_id = tset.id).all()
    return render_template('distributions/dis_main.html',
        title = "Distribuciones", ts_id = tset.id,
        twdis_list = twdis_list, tddis_list = tddis_list)

###### Distribuciones Tópico-Palabra (TopicWordDistribution, twdis)
###################################################################
@app.route("/ts<int:ts_id>/distributions/twdis<int:twdis_id>")
def dis_twdis(ts_id, twdis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one()

    return render_template('distributions/dis_tw.html', ts_id = tset.id, twdis = twdis)

@app.route("/ts<int:ts_id>/distributions/twdis<int:twdis_id>/download")
def dis_twdis_download(ts_id, twdis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one()

    f =""
    f += "<pre>"
    for t in Topic.query.filter_by(topicset_id = ts_id):
        q = db.session.query(TopicWordValue)\
            .filter(TopicWordValue.topicset_id == tset.id)\
            .filter(TopicWordValue.twdis_id == twdis.id)\
            .filter(TopicWordValue.topic_id == t.id)

        f += str(q.count()) + " "
        for elem in q:
            f += "{}:{} ".format(elem.word_id, elem.value)
        f += "\n"
    f+= "</pre>"
    return Response(f, 'text/html')

###### Distribuciones Tópico-Documento (TopicDocumentDistribution, tddis)
###################################################################
@app.route("/ts<int:ts_id>/distributions/tddis<int:tddis_id>")
def dis_tddis(ts_id, tddis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one()

    return render_template('distributions/dis_td.html', ts_id = tset.id, tddis = tddis)

@app.route("/ts<int:ts_id>/distributions/tddis<int:tddis_id>/download")
def dis_tddis_download(ts_id, tddis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one()

    f =""
    f += "<pre>"
    for t in Topic.query.filter_by(topicset_id = ts_id).order_by(Topic.id):
        q = db.session.query(TopicDocumentValue)\
            .filter(TopicDocumentValue.topicset_id == tset.id)\
            .filter(TopicDocumentValue.tddis_id == tddis.id)\
            .filter(TopicDocumentValue.topic_id == t.id)

        f += str(q.count()) + " "
        for elem in q:
            f += "{}:{} ".format(elem.document_id, elem.value)
        f += "\n"
    f+= "</pre>"
    return Response(f, 'text/html')
