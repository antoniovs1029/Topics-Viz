from topics_viz import app, db
from flask import render_template, url_for, redirect, request, Response
from topics_viz.models import *
from topics_viz.models_distributions import *
from topics_viz.templates_python import create_HTML_table

from werkzeug.urls import url_encode

@app.route("/ts<int:ts_id>/exploration")
def exploration(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    return render_template('exploration/exp_main.html',
        title = "Explore", ts_id = tset.id)

@app.route("/ts<int:ts_id>/exploration/topic_table")
def explore_topic_table(ts_id):
    """
    @TODO: Permitir que el ordenadmiento de las columnas también se mantenda al explorar entre tópicos
    """
    col_num = 5
    text=""
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    topic_id = request.args.get('topic_id', 0, type=int)
    t = Topic.query.filter_by(topicset_id = ts_id, id = topic_id).one()

    # CONSTRUYENDO LA TABLA
    table_elements = dict()
    table_headings = ['ID', 'Palabra']
    for word_assoc in t.words:
        table_elements[word_assoc.word.id] = list()
        id_link = "<a href=\"" + url_for('word', ts_id = ts_id, word_id = word_assoc.word.id) + "\">" \
                    + str(word_assoc.word.id)+ "</a>"
        table_elements[word_assoc.word.id].append(id_link)
        table_elements[word_assoc.word.id].append(word_assoc.word.word_string)

    for c in range(1, col_num + 1):
        opt = request.args.get('col' + str(c), "None", type=str)
        if opt ==  "tnum":
            text += "Numero de topicos - "
            table_headings.append('# Tópicos')

            for word_assoc in t.words:
                ntopics = db.session.query(WordTopicsNumber)\
                .filter(WordTopicsNumber.topicset_id == tset.id)\
                .filter(WordTopicsNumber.word_id == word_assoc.word.id)\
                .one().ntopics

                table_elements[word_assoc.word.id].append(int(ntopics))

        elif opt[:5] == "twdis":
            text+= "TWDis " + opt[5:] + " - "
            twdis_id = int(opt[5:])
            twdis = TopicWordDistribution.query.filter_by(topicset_id = ts_id).filter_by(id = twdis_id).one()
            table_headings.append(twdis.name)
            q = TopicWordValue.query.filter_by(topicset_id = ts_id).filter_by(twdis_id = twdis_id).filter_by(topic_id = t.id)
            for elem in q:
                table_elements[elem.word_id].append("{:.4f}".format(elem.value))
        else:
            text+= "Hee - "

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable")

    # PARA EL MENU
    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    return render_template('exploration/exp_topic_table.html',
        title = "Explorar Tópicos", ts_id = tset.id, topic = t,
        col_num = col_num, twdis_list = twdis_list, text =text, table = table)

@app.template_global()
def next_topic_url():
    """
    Para obtener el url del siguiente topico en la "exploracion actual"
    sin perder los parametros GET.
    """
    args = request.args.copy()

    if 'topic_id' in args:
        args['topic_id'] = str(int(args['topic_id']) + 1)
    else:
        args['topic_id'] = str(1) # Hago la suposicion de que si no se tenia indicado el topic_id es porque era el 0

    return '{}?{}'.format(request.path, url_encode(args))

@app.template_global()
def previous_topic_url():
    args = request.args.copy()

    if 'topic_id' in args:
        args['topic_id'] = str(int(args['topic_id']) - 1)
    else:
        args['topic_id'] = str(-1) # Hago la suposicion de que si no se tenia indicado el topic_id es porque era el 0

    return '{}?{}'.format(request.path, url_encode(args))