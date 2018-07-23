from topics_viz import app, db
from topics_viz.models import *
from topics_viz.models_distributions import *

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.io import show

import numpy as np
from sqlalchemy import func

def topicid_nwords_vbar(ts_id):
    """
    Diagrama de barras verticales (vbar) que tiene en el eje 'x' el ID de los Topicos
    de un topicset (con ID ts_id), y en el eje 'y' tiene el número de paralabras
    de cada tópico.
    """
    q = Topic.query.filter_by(topicset_id = ts_id)
    topic_id = [str(x) for x in range(q.count())]

    q2 = db.session.query(Topic.nwords).filter(Topic.topicset_id == ts_id)
    nwords = [x[0] for x in q2]

    data = {'topic_id': topic_id, 'nwords': nwords}

    p = figure(
        x_range= topic_id,
        plot_height=250,
        x_axis_label = "ID de Tópico",
        y_axis_label ="# Palabras",
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        tooltips=[("ID", "@topic_id"), ("# Palabras", "@nwords")]
        )

    p.vbar(
        source = data,
        x = 'topic_id',
        top= 'nwords',
        width=0.9
        )

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    # Para borrar los ticks del eje x:
    p.xaxis.major_label_text_font_size = "0pt"
    p.xaxis.major_tick_in = 0
    p.xaxis.major_tick_out = 0
    return p

def topics_nwords_histogram(ts_id):
    """
    Histograma del numero de palabras en los topicos.
    El tamaño de las bins y del histograma se ajusta automaticamente, para que
    cada bin represente un intervalo de una palabra.
    """
    q2 = db.session.query(Topic.nwords).filter(Topic.topicset_id == ts_id)
    nwords = np.array([x[0] for x in q2])
    hist, edges = np.histogram(nwords, range = (0, nwords.max()), bins = nwords.max())
    data = {'hist': hist, 'left': edges[:-1], 'right': edges[1:]}

    p = figure(plot_height = 600, plot_width = 600,
        x_axis_label = '# Palabras',
        y_axis_label = '# Topicos',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        tooltips=[("# De Topicos:", "@hist"), ("# Palabras", "@left")]
        )

    p.quad(
        source = data,
        bottom=0, top='hist', left='left', right='right'
        )

    return p

def wordid_ntopics_vbar(ts_id):
    """
    Diagrama de barras verticales (vbar) que tiene en el eje 'x' el ID de
    las palabras, y en el eje 'y' el numero de topicos a los que pertenece en un
    topicset.
    """
    q = db.session.query(WordTopicsNumber.ntopics).filter(WordTopicsNumber.topicset_id == ts_id)
    word_id = [str(x) for x in range(q.count())]
    ntopics = [x[0] for x in q]

    data = {'word_id': word_id, 'ntopics': ntopics}

    p = figure(
        x_range= word_id,
        plot_height=250,
        x_axis_label = "ID de la Palabra",
        y_axis_label ="# Topicos",
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        tooltips=[("ID", "@word_id"), ("# Topicos", "@ntopics")]
        )

    p.vbar(
        source = data,
        x = 'word_id',
        top= 'ntopics',
        width=0.9
        )

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    # Para borrar los ticks del eje x:
    p.xaxis.major_label_text_font_size = "0pt"
    p.xaxis.major_tick_in = 0
    p.xaxis.major_tick_out = 0
    return p

def words_ntopics_histogram(ts_id):
    """
    Histograma del numero de tópicos en los que aparece una palabra.
    El tamaño de las bins y del histograma se ajusta automaticamente, para que
    cada bin represente un intervalo de un tópico.
    """
    q = db.session.query(WordTopicsNumber.ntopics).filter(WordTopicsNumber.topicset_id == ts_id)
    ntopics = np.array([x[0] for x in q])
    hist, edges = np.histogram(ntopics, range = (0, ntopics.max()), bins = ntopics.max())
    data = {'hist': hist, 'left': edges[:-1], 'right': edges[1:]}
    interval = ['De {} a {} tópicos'.format(x, y) for x, y in zip(data['left'], data['right'])]
    data['interval'] = interval

    p = figure(plot_height = 600, plot_width = 600,
        x_axis_label = '# Tópicos',
        y_axis_label = '# Palabras',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        tooltips=[("# De Palabras:", "@hist"), ("# Topicos", "@left")]
        )

    p.quad(
        source = data,
        bottom=0, top='hist', left='left', right='right'
        )

    return p

def twdis_summary(ts_id, twdis_id):
    """
    """
    ids = []
    maxes = []
    mins = []
    avgs = []
    nwords = []
    for topic in Topic.query.filter_by(topicset_id = ts_id):
        ids.append(str(topic.id))
        tmax, tmin, tavg = db.session.query(
            func.max(TopicWordValue.value),
            func.min(TopicWordValue.value),
            func.avg(TopicWordValue.value)
            )\
            .filter(TopicWordValue.topicset_id == ts_id)\
            .filter(TopicWordValue.twdis_id == twdis_id)\
            .filter(TopicWordValue.topic_id == topic.id)\
            .one()
        maxes.append(tmax)
        mins.append(tmin)
        avgs.append(tavg)
        nwords.append(topic.nwords)

    p = figure(plot_height = 300, plot_width = 600,
        x_axis_label = 'ID de Tópico',
        y_axis_label = 'Valor',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        x_range=[0,len(ids)]
        )

    p.line(ids, maxes, legend="Máximo", line_color="red")
    p.line(ids, mins, legend="Mínimo", line_color="blue")
    p.line(ids, avgs, legend="Promedio", line_color="green")
    #p.multi_line(
    #    xs = [ids, ids, ids],
    #    ys = [maxes, mins, avgs],
    #    line_color = ['#FF0000', '#0087FF', '#1D702D']
    #    )

    p2 = figure(plot_height = 300, plot_width = 600,
        x_axis_label = 'ID de Tópico',
        y_axis_label = '# Palabras',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        x_range=p.x_range
        )

    p2.line(ids, nwords, line_color="black")

    return p, p2

def twdis_topic(ts_id, twdis_id, topic_id):
    """
    """
    ids = []
    words = []
    values = []

    q = db.session.query(TopicWordValue)\
        .filter(TopicWordValue.topicset_id == ts_id)\
        .filter(TopicWordValue.twdis_id == twdis_id)\
        .filter(TopicWordValue.topic_id == topic_id)\
        .order_by(TopicWordValue.word_id)

    for i, elem in enumerate(q):
        ids.append(i)
        words.append(Word.query.filter_by(id = elem.word_id).one().word_string)
        values.append(elem.value)

    panorama = figure(plot_height = 200, plot_width = 600,
        x_axis_label = 'Palabras (ordenadas por ID)',
        y_axis_label = 'Valor',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        x_range=[-2,len(ids)]
        )

    panorama.line(ids, values)

    data = {'id': ids, 'word': words, 'value': values}

    full = figure(
        y_range= words,
        plot_width=600,
        x_axis_label = "Valor",
        y_axis_label ="Palabras (ordenadas por ID)",
        tools="ypan, ywheel_zoom, ywheel_pan, box_zoom, reset, save",
        tooltips=[("Palabra", "@word"), ("Valor", "@value"), ("ID", "@id")]
        )

    full.hbar(
        source = data,
        y = 'word',
        right = 'value',
        height=0.5
        )

    return panorama, full

def tddis_summary(ts_id, tddis_id):
    """
    """
    ids = []
    maxes = []
    mins = []
    avgs = []
    counts = []
    nwords = []
    for topic in Topic.query.filter_by(topicset_id = ts_id):
        ids.append(str(topic.id))
        tmax, tmin, tavg, tcount = db.session.query(
            func.max(TopicDocumentValue.value),
            func.min(TopicDocumentValue.value),
            func.avg(TopicDocumentValue.value),
            func.count(TopicDocumentValue.value)
            )\
            .filter(TopicDocumentValue.topicset_id == ts_id)\
            .filter(TopicDocumentValue.tddis_id == tddis_id)\
            .filter(TopicDocumentValue.topic_id == topic.id)\
            .one()
        maxes.append(tmax)
        mins.append(tmin)
        avgs.append(tavg)
        counts.append(tcount)
        nwords.append(topic.nwords)

    p1 = figure(plot_height = 300, plot_width = 600,
        x_axis_label = 'ID de Tópico',
        y_axis_label = '# Documentos Relacionados',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        x_range=[0,len(ids)]
        )
    p1.line(ids, counts, line_color="black")

    p2 = figure(plot_height = 300, plot_width = 600,
        x_range = p1.x_range,
        x_axis_label = 'ID de Tópico',
        y_axis_label = 'Valor',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        )

    p2.line(ids, maxes, legend="Máximo", line_color="red")
    p2.line(ids, mins, legend="Mínimo", line_color="blue")
    p2.line(ids, avgs, legend="Promedio", line_color="green")

    p3 = figure(plot_height = 300, plot_width = 600,
        x_range = p1.x_range,
        x_axis_label = 'ID de Tópico',
        y_axis_label = '# Palabras',
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        )

    p3.line(ids, nwords, line_color="black")

    #p.multi_line(
    #    xs = [ids, ids, ids],
    #    ys = [maxes, mins, avgs],
    #    line_color = ['#FF0000', '#0087FF', '#1D702D']
    #    )
    return (p1, p2, p3)

def tddis_topic(ts_id, tddis_id, topic_id):
    """
    """
    ids = []
    doc_ids = []
    titles = []
    values = []

    q = db.session.query(TopicDocumentValue)\
        .filter(TopicDocumentValue.topicset_id == ts_id)\
        .filter(TopicDocumentValue.tddis_id == tddis_id)\
        .filter(TopicDocumentValue.topic_id == topic_id)\
        .order_by(TopicDocumentValue.document_id)

    for i, elem in enumerate(q):
        ids.append(i)
        doc_ids.append(str(elem.document_id))
        titles.append(Document.query.filter_by(id = elem.document_id).one().title)
        values.append(elem.value)

    panorama1 = figure(plot_height = 200, plot_width = 600,
        x_axis_label = 'Documentos (ordenados por ID)',
        y_axis_label = 'Valor',
        x_range=[-2,len(ids)],
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        )

    panorama1.line(ids, values)

    data = {'doc_id': doc_ids, 'title': titles, 'value': values}

    full = figure(
        y_range= doc_ids,
        plot_width=600,
        x_axis_label = "Valor",
        y_axis_label ="Documentos (ordenadas por ID)",
        tools="ypan, ywheel_zoom, ywheel_pan, box_zoom, reset, save",
        tooltips=[("Titulo", "@title"), ("Valor", "@value"), ("ID", "@doc_id")]
        )

    full.hbar(
        source = data,
        y = 'doc_id',
        right = 'value',
        height=0.5
        )

    return panorama1, full
