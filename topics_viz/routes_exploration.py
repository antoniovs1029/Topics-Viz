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

from bokeh.embed import components
import pandas as pd

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

    # CONSTRUYENDO LA TABLA
    table_elements = dict()
    table_headings = ['WORD_ID', 'WORD']
    for word_assoc in t.words:
        table_elements[word_assoc.word.id] = list()
        table_elements[word_assoc.word.id].append(word_assoc.word_id)
        table_elements[word_assoc.word.id].append(word_assoc.word.word_string)

    plot_columns = []
    columns_names = []
    for c in range(1, col_num + 1):
        opt = request.args.get('col' + str(c), "None", type=str)
        if opt ==  "tnum":
            table_headings.append('COL_' + str(c)) # es necesario renombrar las columnas, pues si dos columnas (distribuciones) se llamaran igual, habria problemas en el ploteo
            plot_columns.append('COL_' + str(c))
            columns_names.append("#" + str(c) + ": # Tópicos")

            for word_assoc in t.words:
                ntopics = db.session.query(WordTopicsNumber)\
                .filter(WordTopicsNumber.topicset_id == tset.id)\
                .filter(WordTopicsNumber.word_id == word_assoc.word.id)\
                .one().ntopics

                table_elements[word_assoc.word.id].append(int(ntopics))

        elif opt[:5] == "twdis":
            twdis_id = int(opt[5:])
            twdis = TopicWordDistribution.query.filter_by(topicset_id = ts_id).filter_by(id = twdis_id).one()
            table_headings.append('COL_' + str(c))
            plot_columns.append('COL_' + str(c))
            columns_names.append("#" + str(c) + ": " + twdis.name)

            q = TopicWordValue.query.filter_by(topicset_id = ts_id).filter_by(twdis_id = twdis_id).filter_by(topic_id = t.id)
            for elem in q:
                table_elements[elem.word_id].append(elem.value)

    data = pd.DataFrame.from_dict(table_elements, orient='index', columns= table_headings)

    order_by = request.args.get('order_by', "WORD_ID", type=str)
    print(order_by)
    data = data.sort_values([order_by], ascending = False)
    print(data)
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
    if plot_columns:
        panorama = plotter.plot_panorama(data, plot_columns, columns_names, colors, x_axis_label = plot_label, y_axis_label = "Valor")
        hbar = plotter.plot_hbars(data, plot_columns, columns_names, colors, tooltips = tooltips, x_axis_label = "Valores", y_axis_label = plot_label)
        script, div = components((panorama, hbar))
    else:
        div = "<p>Escoger los datos a mostrar en el panel derecho</p>"
        script = "<p></p>"

    # PARA EL MENU
    twdis_list = TopicWordDistribution.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(TopicWordDistribution.id)

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

#########################################
### Global templates de jinja para hacer que los botones de navegacion
### mantengan los parametros del GET request
#########################################

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
