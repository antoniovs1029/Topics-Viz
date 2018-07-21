from topics_viz import app, db
from topics_viz.models import *
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
import numpy as np

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
    interval = ['De {} a {} palabras'.format(x, y) for x, y in zip(data['left'], data['right'])]
    data['interval'] = interval

    p = figure(plot_height = 600, plot_width = 600,
        x_axis_label = '# Palabras',
        y_axis_label = '# Topicos',
        tools="xpan, xwheel_zoom, box_zoom, reset, save",
        tooltips=[("# De Topicos:", "@hist"), ("Intervalo", "@interval")]
        )

    p.quad(
        source = data,
        bottom=0, top='hist', left='left', right='right'
        )

    return p
