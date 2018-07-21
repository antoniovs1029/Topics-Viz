from topics_viz import app, db
from topics_viz.models import *

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
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
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
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
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
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
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
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
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

    p = figure(plot_height = 600, plot_width = 600,
        x_axis_label = 'ID de Tópico',
        y_axis_label = 'Valor',
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
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
    print(len(ids))
    return p

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
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
        x_range=[-2,len(ids)]
        )

    panorama.line(ids, values)

    data = {'id': ids, 'word': words, 'value': values}

    full = figure(
        y_range= words,
        plot_width=600,
        x_axis_label = "Valor",
        y_axis_label ="Palabras (ordenadas por ID)",
        tools="ypan, ywheel_zoom, box_zoom, reset, save",
        tooltips=[("Palabra", "@word"), ("Valor", "@value"), ("ID", "@id")]
        )

    full.hbar(
        source = data,
        y = 'word',
        right = 'value',
        height=0.5
        )

    return panorama, full
