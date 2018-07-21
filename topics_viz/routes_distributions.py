from topics_viz import app, db
from flask import render_template, url_for, redirect, request, Response
from topics_viz.models import *
from topics_viz.templates_python import create_HTML_table

@app.route("/ts<int:ts_id>/distributions")
def distributions(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis_list = TopicWordDistribution.query.filter_by(topicset_id = tset.id).all()
    return render_template('distributions/dis_main.html', title = "Distribuciones", ts_id = tset.id, twdis_list = twdis_list)

@app.route("/ts<int:ts_id>/distributions/twdis<int:twdis_id>")
def dis_twdis(ts_id, twdis_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one()

    return render_template('distributions/dis_tw.html', ts_id = tset.id, twdis = twdis)

@app.route("/ts<int:ts_id>/distributions/twdis<int:twdis_id>/table/topic<int:topic_id>")
def dis_twdis_table(ts_id, twdis_id, topic_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one()
    t = Topic.query.filter_by(topicset_id = ts_id).filter_by(id = topic_id).one()

    table_elements = dict()
    table_headings = ['ID', 'Palabra', 'No. Tópicos']
    for word_assoc in t.words:
        table_elements[word_assoc.word.id] = list()
        id_link = "<a href=\"" + url_for('word', ts_id = ts_id, word_id = word_assoc.word.id) + "\">" \
                    + str(word_assoc.word.id)+ "</a>"
        table_elements[word_assoc.word.id].append(id_link)
        table_elements[word_assoc.word.id].append(word_assoc.word.word_string)

        ntopics = db.session.query(WordTopicsNumber)\
                    .filter(WordTopicsNumber.topicset_id == tset.id)\
                    .filter(WordTopicsNumber.word_id == word_assoc.word.id)\
                    .one().ntopics

        table_elements[word_assoc.word.id].append(int(ntopics))

    table_headings.append(twdis.name)
    q = TopicWordValue.query.filter_by(topicset_id = tset.id)\
        .filter_by(twdis_id = twdis.id, topic_id = topic_id)

    for v in q:
        table_elements[v.word_id].append("{:.4f}".format(v.value))

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable", classes= "responsive-table")

    return render_template('distributions/dis_tw_table.html', ts_id = tset.id, twdis = twdis, topic = t, table = table)

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
    print(f[0:10])
    return Response(f, 'text/html')
