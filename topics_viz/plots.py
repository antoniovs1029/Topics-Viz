"""
@TODO: Que en los plots no se hagan queries, sino que se pasen datos (quizas
en forma de dataframe de pandas) y luego se hagan los plots.
"""

from topics_viz import app, db
from topics_viz.models import *
from topics_viz.models_distributions import *

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.io import show
from bokeh.core.properties import value
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.models import BasicTicker, PrintfTickFormatter, ColorBar
from bokeh.palettes import Viridis10

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

def plot_panorama(data, columns, legends, colors, x_axis_label = "Elementos", y_axis_label = "Valores"):
    """
    data: un dataframe de pandas con los datos a plotear. Debe tener una columna llamada "ROW_ID"
    que indique el orden en que deberán ser plotados los elementos.

    columns: lista con las cadenas con los nombres de las columnas a plotear

    colors: lista de strings, que deberá ser mínimo del tamaño de 'columns',
    indicando colores a usar para plotear

    x_axis_label y y_axis_label las etiquetas del plot.

    colors es una lista con 'n' cadenas, donde las cadenas representan los colores
    de las lineas.

    La implementación actual solo tiene 5 colores para las líneas,
    (por tanto, 'n' deberá ser máximo 5)
    """

    panorama = figure(plot_height = 200, plot_width = 600,
        x_axis_label = x_axis_label,
        y_axis_label = y_axis_label,
        tools="xpan, xwheel_zoom, xwheel_pan, box_zoom, reset, save",
        toolbar_location = "above",
        x_range=[-2, data.shape[0]]
        )

    for i, column in enumerate(columns):
        panorama.line(source = data, x = 'ROW_ID', y = column, legend = value(legends[i]), line_color = colors[i])

    return panorama

def plot_hbars(data, columns, legends, colors, tooltips = [], x_axis_label = "Valores", y_axis_label = "Elementos"):
    p = figure(
        y_range = data['WORD'][::-1], #@TODO: Pasar como parametro que columna se tomará como categórica
        plot_width = 600,
        plot_height = max(len(data)*15*len(columns), 300),
        x_axis_label = x_axis_label,
        y_axis_label = y_axis_label,
        tools="ypan, ywheel_zoom, ywheel_pan, box_zoom, reset, save",
        tooltips= tooltips
        )

    dodging_factor = 1 / (2*len(columns)) #@TODO: Quizás no sea la mejor manera de hacer esto
    dodging = 0 - dodging_factor*len(columns)/2
    for i, column in enumerate(columns):
        p.hbar(
            source = data,
            y = dodge('WORD', dodging, range=p.y_range),
            right = column,
            height= (1 - .1)/len(columns),
            color = colors[i],
            legend = value(legends[i])
            )
        dodging += dodging_factor

    p.y_range.range_padding = 0.1

    return p

def plot_twdis_heatmap(heatmap_data):
    color_palette = Viridis10.copy()
    color_palette.reverse()
    color_mapper = LinearColorMapper(palette=color_palette, low=min(heatmap_data['value']), high=max(heatmap_data['value']))

    data_source = ColumnDataSource(heatmap_data)
    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

    p = figure(
                plot_height=500,
                plot_width=1000,
                x_axis_label = "ID de Tópico",
                y_axis_label ="ID de Palabra",
                tools=TOOLS,
                tooltips=[("Word ID", "@word_id"), ("Topic ID", "@topic_id"), ("Valor", "@value")]
                )

    p.scatter(source = data_source,
        x='topic_id', y='word_id',
        size= 3.5,
        fill_color = {'field': 'value', 'transform': color_mapper},
        line_color = None)

    color_bar = ColorBar(color_mapper=color_mapper, major_label_text_font_size="5pt",
                     ticker=BasicTicker(desired_num_ticks=len(color_palette)),
                     label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    return p

def plot_twdis_correlations(data, labels):
    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

    p = figure(
                plot_height=500,
                plot_width=1000,
                x_axis_label = labels[0],
                y_axis_label = labels[1],
                tools=TOOLS,
                tooltips=[("Word ID", "@word_id"), ("Topic ID", "@topic_id"), ("X", "@x"), ("Y", "@y")]
                )

    p.scatter(source = data,
        x='x', y='y',
        size= 3.5,
        line_color = None)

    return p