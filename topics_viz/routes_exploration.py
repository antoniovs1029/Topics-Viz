"""
@TODO: Separar la obtención de datos a otro modulo, donde se obtengan los
datos y quizás se use un dataframe de pandas para almacenarlos (usando
la función .read_sql)
"""

from topics_viz import app, db
from flask import render_template, url_for, redirect, request, Response
from topics_viz.models import *
from topics_viz.models_distributions import *
from topics_viz.templates_python import create_HTML_table
import topics_viz.plots as plotter

from sqlalchemy import func as sqlfunc

import random
from collections import defaultdict

from bokeh.embed import components
import pandas as pd

from werkzeug.urls import url_encode

###### Menú principal de explorations
###################################################################
@app.route("/ts<int:ts_id>/exploration")
def exploration(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    return render_template('exploration/exp_main.html',
        title = "Explore", ts_id = tset.id)

###### Sobre # de tópicos y # de palabras
###################################################################
@app.route("/ts<int:ts_id>/exploration/plots_topics_nwords")
def plot_topics_nwords(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.topicid_nwords_vbar(ts_id)
    p2 = plotter.topics_nwords_histogram(ts_id)
    script, div = components((p, p2))
    return render_template('exploration/plots_topics-nwords.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

@app.route("/ts<int:ts_id>/exploration/plots_words_ntopics")
def plot_words_ntopics(ts_id):
    """
    @TODO: Hay un bug en el histograma. Por alguna razón junta los últimos 2 bins (los bins con el número de tópicos mas grande).
    Por ejemplo, en el bin de palabras con 6 tópicos pone las palabras con 6 o 7 tópicos (siendo 7 el mayor)
    """
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    p = plotter.wordid_ntopics_vbar(ts_id)
    p2 = plotter.words_ntopics_histogram(ts_id)
    script, div = components((p, p2))
    return render_template('exploration/plots_words-ntopics.html', ts_id = ts_id,
        script = script, div = div[0], div2 = div[1])

###### Distribuciones Tópico-Palabra (TopicWordDistribution, twdis)
###################################################################
@app.route("/ts<int:ts_id>/exploration/topic_table")
def explore_topic_table(ts_id):
    """
    @TODO: Permitir que el ordenadmiento de las columnas también se mantenda al explorar entre tópicos
    """
    col_num = 5
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
            table_headings.append('# Tópicos')

            for word_assoc in t.words:
                ntopics = db.session.query(WordTopicsNumber)\
                .filter(WordTopicsNumber.topicset_id == tset.id)\
                .filter(WordTopicsNumber.word_id == word_assoc.word.id)\
                .one().ntopics

                table_elements[word_assoc.word.id].append(int(ntopics))

        elif opt[:5] == "twdis":
            twdis_id = int(opt[5:])
            twdis = TopicWordDistribution.query.filter_by(topicset_id = ts_id).filter_by(id = twdis_id).one()
            table_headings.append(twdis.name)
            q = TopicWordValue.query.filter_by(topicset_id = ts_id).filter_by(twdis_id = twdis_id).filter_by(topic_id = t.id)
            for elem in q:
                table_elements[elem.word_id].append("{:.4f}".format(elem.value))
        # else # do nothing

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable")

    # PARA EL MENU
    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    return render_template('exploration/exp_topic_table.html',
        title = "Explorar Tópicos", ts_id = tset.id, topic = t,
        col_num = col_num, twdis_list = twdis_list, table = table)

@app.route("/ts<int:ts_id>/exploration/topic_graph")
def explore_topic_graph(ts_id):
    """
    @TODO: Hay un bug cuando se grafica un topico de 300 palabras, con 5
    columnas seleccionadas, y no se muestran todas las barras por alguna razón.
    Pero por alguna razón sí aparecen todos los tooltips.
    """
    col_num = 5
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    topic_id = request.args.get('topic_id', 0, type=int)
    t = Topic.query.filter_by(topicset_id = ts_id, id = topic_id).one()

    # PARA EL MENU
    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    # CONSTRUYENDO LA TABLA
    table_elements = dict()
    table_headings = ['WORD_ID', 'WORD']
    for word_assoc in t.words:
        table_elements[word_assoc.word.id] = list()
        table_elements[word_assoc.word.id].append(word_assoc.word_id)
        table_elements[word_assoc.word.id].append(word_assoc.word.word_string)

    normalize = False
    if request.args.get('normalize', "no", type=str) == "yes":
        normalize = True

    plot_columns = []
    columns_names = []
    for c in range(1, col_num + 1):
        opt = request.args.get('col' + str(c), "None", type=str)
        if opt ==  "tnum":
            table_headings.append('COL_' + str(c)) # es necesario renombrar las columnas, pues si dos columnas (distribuciones) se llamaran igual, habria problemas en el ploteo
            plot_columns.append('COL_' + str(c))
            columns_names.append("#" + str(c) + ": # Tópicos")

            normalize_factor = 1
            if normalize :
                normalize_factor = db.session.query(sqlfunc.max(WordTopicsNumber.ntopics))\
                                .filter(WordTopicsNumber.topicset_id == tset.id)\
                                .one()[0]


            for word_assoc in t.words:
                ntopics = db.session.query(WordTopicsNumber)\
                .filter(WordTopicsNumber.topicset_id == tset.id)\
                .filter(WordTopicsNumber.word_id == word_assoc.word.id)\
                .one().ntopics

                table_elements[word_assoc.word.id].append(ntopics/normalize_factor)

        elif opt[:5] == "twdis":
            twdis_id = int(opt[5:])
            twdis = TopicWordDistribution.query.filter_by(topicset_id = ts_id).filter_by(id = twdis_id).one()
            table_headings.append('COL_' + str(c))
            plot_columns.append('COL_' + str(c))
            columns_names.append("#" + str(c) + ": " + twdis.name)

            normalize_factor = 1
            if normalize:
                normalize_factor = twdis.normalization_value

            q = TopicWordValue.query.filter_by(topicset_id = ts_id).filter_by(twdis_id = twdis_id).filter_by(topic_id = t.id)
            for elem in q:
                table_elements[elem.word_id].append(elem.value / normalize_factor)

    if not plot_columns:
        return render_template('exploration/exp_topic_graph.html',
            title = "Explorar Tópicos", ts_id = tset.id, topic = t,
            col_num = col_num, twdis_list = twdis_list, message= "Escoger los datos a graficar en el panel de la derecha")

    data = pd.DataFrame.from_dict(table_elements, orient='index', columns= table_headings)

    order_by = request.args.get('order_by', "WORD_ID", type=str)
    data = data.sort_values([order_by], ascending = False)
    data['ROW_ID'] = range(1, len(data) + 1)
    #print(data)

    plot_label = "Palabras (ordenadas por "
    if order_by == "WORD_ID":
        plot_label += " Word ID)"
    else:
        plot_label += "Datos #" + order_by[4:] + ")"

    colors = ["blue", "red", "green", "black", "pink"] # en la implementacion actual solo se consideran maximo 5 columnas (y cinco colores)
    tooltips = [("Word ID", "@WORD_ID"), ("Word:", "@WORD")]
    for i, column in enumerate(plot_columns):
        tt = (columns_names[i], "@" + column)
        tooltips.append(tt)

    y_label = "Valor"
    if normalize:
        y_label = "Valor Normalizado"

    panorama = plotter.plot_panorama(data, plot_columns, columns_names, colors, x_axis_label = plot_label, y_axis_label = y_label)
    hbar = plotter.plot_hbars(data, plot_columns, columns_names, colors, tooltips = tooltips, x_axis_label = y_label, y_axis_label = plot_label)
    script, div = components((panorama, hbar))

    return render_template('exploration/exp_topic_graph.html',
        title = "Explorar Tópicos", ts_id = tset.id, topic = t,
        col_num = col_num, twdis_list = twdis_list, table = None,
        script = script, div = div[0], div2 = div[1])

@app.route("/ts<int:ts_id>/exploration/word_table")
def explore_word_table(ts_id):
    col_num = 5
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    word_id = request.args.get('word_id', 0, type=int)
    word = Word.query.filter_by(id = word_id).one()
    ntopics = WordTopicsNumber.query.filter_by(topicset_id = ts_id)\
        .filter_by(word_id = word_id)\
        .one().ntopics

    q1 = TopicWordAssociation.query.\
        filter_by(topicset_id = ts_id).\
        filter_by(word_id = word.id).\
        order_by(TopicWordAssociation.topic_id)

    table_elements = dict()
    table_headings = ['Topic ID']
    for word_assoc in q1:
        table_elements[word_assoc.topic_id] = list()
        id_link = "<a href=\"" + url_for('topic', ts_id = ts_id, topic_id = word_assoc.topic_id) + "\">" \
                    + str(word_assoc.topic_id)+ "</a>"
        table_elements[word_assoc.topic_id].append(id_link)

    for c in range(1, col_num + 1):
        opt = request.args.get('col' + str(c), "None", type=str)
        if opt ==  "wnum":
            table_headings.append('# Palabras')
            for word_assoc in q1:
                table_elements[word_assoc.topic_id].append(word_assoc.topic.nwords)

        elif opt[:5] == "twdis":
            twdis_id = int(opt[5:])
            twdis = TopicWordDistribution.query.filter_by(topicset_id = ts_id).filter_by(id = twdis_id).one()
            table_headings.append(twdis.name)
            q = TopicWordValue.query.filter_by(topicset_id = ts_id).filter_by(twdis_id = twdis_id).filter_by(word_id = word.id)
            for elem in q:
                table_elements[elem.topic_id].append("{:.4f}".format(elem.value))

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable")

    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    return render_template('exploration/exp_word_table.html',
            title = "Explorar Palabras", ts_id = tset.id, word = word, ntopics = ntopics,
            col_num = col_num, twdis_list = twdis_list, table = table)

@app.route("/ts<int:ts_id>/exploration/twdis_summary")
def explore_twdis_summary(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    twdis_id = request.args.get('twdis_id', -1, type=int)
    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    if twdis_id == -1:
        return render_template('exploration/exp_twdis_summary.html', ts_id = ts_id,
            message = "Escoger la distribución en el panel izquierdo", twdis_list = twdis_list)

    twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one() # para que si no existe la twdis suceda un error

    p1, p2 = plotter.twdis_summary(ts_id, twdis_id)
    script, div = components((p1, p2))

    return render_template('exploration/exp_twdis_summary.html', ts_id = ts_id,
        twdis = twdis, script = script, div = div[0], div2 = div[1], twdis_list = twdis_list)

@app.route("/ts<int:ts_id>/exploration/twdis_heatmap")
def explore_twdis_heatmap(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    twdis_id = request.args.get('twdis_id', -1, type=int)

    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    word_id = []
    topic_id = []
    value = []
    if twdis_id == -1:
        q = TopicWordAssociation.query.filter_by(topicset_id = tset.id)
        word_id = []
        topic_id = []

        for elem in q:
            word_id.append(elem.word_id)
            topic_id.append(elem.topic_id)
            value.append(elem.topic_id)

        npuntos = q.count()
    else:
        twdis = db.session.query(TopicWordDistribution)\
        .filter(TopicWordDistribution.topicset_id == tset.id)\
        .filter(TopicWordDistribution.id == twdis_id).one() # para que si no existe la twdis suceda un error

        q = TopicWordValue.query.filter_by(topicset_id = tset.id, twdis_id = twdis.id)

        for elem in q:
            word_id.append(elem.word_id)
            topic_id.append(elem.topic_id)
            value.append(elem.value)

        npuntos = q.count()

    p = plotter.plot_twdis_heatmap({'word_id': word_id, 'topic_id': topic_id, 'value': value})

    script, div = components(p)    

    return render_template('exploration/exp_twdis_heatmap.html', ts_id = ts_id,
        script = script, div = div, npuntos = npuntos, twdis_list = twdis_list)

@app.route("/ts<int:ts_id>/exploration/twdis_correlations")
def explore_twdis_correlations(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()

    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

    word_id = []
    topic_id = []
    value = []

    d = defaultdict(list)

    q = TopicWordAssociation.query.filter_by(topicset_id = tset.id)
    for elem in q:
        d[(elem.topic_id, elem.word_id)].append(elem.topic_id)
        d[(elem.topic_id, elem.word_id)].append(elem.word_id)

    npuntos = q.count()

    x_axis_id = request.args.get('x', -1, type=int)
    y_axis_id = request.args.get('y', -2, type=int)

    axis = [x_axis_id, y_axis_id]
    labels = []
    for twdis_id in axis:
        if twdis_id == -1:
            for k in d.keys(): #@TODO: Quizas esto es mejor hacerlo con un "map" o algo así
                d[k].append(d[k][0])
            labels.append("ID. Topico")
        elif twdis_id == -2:
            for k in d.keys():
                d[k].append(d[k][1])
            labels.append("ID. Palabras")
        else:
            twdis = db.session.query(TopicWordDistribution)\
            .filter(TopicWordDistribution.topicset_id == tset.id)\
            .filter(TopicWordDistribution.id == twdis_id).one() # para que si no existe la twdis suceda un error

            q = TopicWordValue.query.filter_by(topicset_id = tset.id, twdis_id = twdis.id)

            for elem in q:
                d[(elem.topic_id), (elem.word_id)].append(elem.value)

            labels.append(twdis.name)


    df = pd.DataFrame([ x for x in d.values()],
        columns=['topic_id', 'word_id', 'x', 'y'])

    p = plotter.plot_twdis_correlations(df, labels)

    script, div = components(p)    

    return render_template('exploration/exp_twdis_correlations.html', ts_id = ts_id,
        script = script, div = div, npuntos = npuntos, twdis_list = twdis_list)

###### Distribuciones Tópico-Documento (TopicDocumentDistribution, tddis)
###################################################################
@app.route("/ts<int:ts_id>/exploration/tddis_topic_table")
def explore_tddis_topic_table(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    tddis_id = request.args.get('tddis_id', -1, type=int)
    topic_id = request.args.get('topic_id', 0, type= int)
    t = Topic.query.filter_by(topicset_id = ts_id).filter_by(id = topic_id).one()

    # PARA EL MENU:
    tddis_list = TopicDocumentDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicDocumentDistribution.id)

    if tddis_id == -1:
        return render_template('exploration/exp_tddis_topic_table.html', ts_id = tset.id,
            topic = t, message = "Escoger distribución en el panel izquierdo",
            tddis_list = tddis_list)

    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one()

    table_elements = dict()
    table_headings = ['ID', 'Titulo', tddis.name]
    q = TopicDocumentValue.query.filter_by(topicset_id = tset.id)\
        .filter_by(tddis_id = tddis.id, topic_id = topic_id)

    for elem in q:
        table_elements[elem.document_id] = list()
        table_elements[elem.document_id].append(str(elem.document_id))
        doc = db.session.query(Document).filter(Document.id == elem.document_id).one()
        table_elements[elem.document_id].append(doc.title)
        table_elements[elem.document_id].append("{:.4f}".format(elem.value))

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable")
    return render_template('exploration/exp_tddis_topic_table.html', ts_id = tset.id,
        tddis = tddis, topic = t, table = table, dnum = len(table_elements),
        tddis_list = tddis_list)

@app.route("/ts<int:ts_id>/exploration/tddis_topic_graph")
def explore_tddis_topic_graph(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    tddis_id = request.args.get('tddis_id', -1, type=int)
    topic_id = request.args.get('topic_id', 0, type= int)
    topic = Topic.query.filter_by(topicset_id = ts_id).filter_by(id = topic_id).one()

    # PARA EL MENU:
    tddis_list = TopicDocumentDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicDocumentDistribution.id)

    if tddis_id == -1:
        return render_template('exploration/exp_tddis_topic_graph.html', ts_id = tset.id,
            topic = topic, message = "Escoger distribución en el panel izquierdo",
            tddis_list = tddis_list)

    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one() # para que si no existe la tddis suceda un error


    panorama, full = plotter.tddis_topic(ts_id, tddis_id, topic_id)
    script, div = components((panorama, full))
    return render_template('exploration/exp_tddis_topic_graph.html', ts_id = ts_id,
        tddis = tddis, topic = topic, script = script, div = div[0], div2 = div[1],
        tddis_list = tddis_list)

@app.route("/ts<int:ts_id>/exploration/tddis_summary")
def explore_tddis_summary(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one()
    tddis_id = request.args.get('tddis_id', -1, type=int)
    tddis_list = TopicDocumentDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicDocumentDistribution.id)

    if tddis_id == -1:
        return render_template('exploration/exp_tddis_summary.html', ts_id = ts_id,
            message = "Escoger la distribución en el panel izquierdo", tddis_list = tddis_list)

    tddis = db.session.query(TopicDocumentDistribution)\
        .filter(TopicDocumentDistribution.topicset_id == tset.id)\
        .filter(TopicDocumentDistribution.id == tddis_id).one() # para que si no existe la twdis suceda un error

    p1, p2, p3 = plotter.tddis_summary(ts_id, tddis_id)
    script, div = components((p1, p2, p3))
    return render_template('exploration/exp_tddis_summary.html', ts_id = ts_id,
        tddis = tddis, script = script, div1 = div[0], div2 = div[1], div3 = div[2], tddis_list = tddis_list)

#############################################################################
### Global templates de jinja para hacer que los botones de navegacion
### mantengan los parametros del GET request
############################################################################

@app.template_global()
def next_item_url(item_id):
    args = request.args.copy()

    if item_id in args:
        args[item_id] = str(int(args[item_id]) + 1)
    else:
        args[item_id] = str(1) # Hago la suposicion de que si no se tenia indicado el item_id es porque era el 0

    return '{}?{}'.format(request.path, url_encode(args))

@app.template_global()
def previous_item_url(item_id):
    args = request.args.copy()

    if item_id in args:
        args[item_id] = str(int(args[item_id]) - 1)
    else:
        args[item_id] = str(-1) # Hago la suposicion de que si no se tenia indicado el topic_id es porque era el 0

    return '{}?{}'.format(request.path, url_encode(args))
