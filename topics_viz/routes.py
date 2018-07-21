import time

from topics_viz import app, db
from flask import render_template, url_for, redirect, request

from topics_viz.models import *
from topics_viz.forms import SearchForm
from topics_viz.templates_python import create_HTML_table


@app.route("/")
@app.route("/home")
def home():
    c = Corpus.query.first()
    return render_template('home.html', title="Topics-Viz", corpus = c, topic_sets = TopicSet.query)

@app.route("/ts<int:ts_id>")
@app.route("/ts<int:ts_id>/topics/home")
def topics_home(ts_id):
    return redirect(url_for('topics', ts_id = ts_id))

@app.route("/ts<int:ts_id>/topics")
def topics(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    page = request.args.get('page', 1, type=int)
    results = Topic.query.filter_by(topicset_id = tset.id).order_by(Topic.id).paginate(per_page = 50, page = page)
    return render_template('topics.html', title="Topicos", ts_id = tset.id, results = results)

@app.route("/<int:ts_id>/topics_all")
def topics_all(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    table_elements = dict()
    table_headings = ['ID', 'No. Palabras', 'Palabras Ejemplo']
    MAX_WORDS = 7

    for topic in Topic.query.filter_by(topicset_id = tset.id):
        table_elements[topic.id] = list()
        topic_link = "<a href=\"" + url_for('topic', ts_id = tset.id, topic_id = topic.id) + "\">" \
                        + str(topic.id) + "</a>"
        table_elements[topic.id].append(topic_link)
        table_elements[topic.id].append(topic.nwords)
        word_list = ""
        for word_assoc in topic.words[:MAX_WORDS]:
            word_list += str(word_assoc.word.word_string) + ", "
        word_list += "..."

        table_elements[topic.id].append(word_list)

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable", classes= "responsive-table")

    return render_template('topics_all.html', title="Topicos", ts_id = tset.id, tnum = len(table_elements), table = table)

"""
@app.route("/topics_all")
def topics_all():
    topic_list = Topic.query.all()
    return render_template('topics_all.html', title="Topicos", tnum = len(topic_list), topic_list = topic_list)
"""

@app.route("/ts<int:ts_id>/topic/<int:topic_id>")
def topic(ts_id, topic_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    t = Topic.query.filter_by(topicset_id = tset.id).filter_by(id=topic_id).one()

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

    """
    # Si se quiere añadir todas las distribuciones a la tabla:
    for twdis in TopicWordDistribution.query.filter_by(topicset_id = tset.id):
        table_headings.append(twdis.name)
        for v in TopicWordValue.query\
            .filter_by(topicset_id = tset.id)\
            .filter_by(twdis_id = twdis.id, topic_id = topic_id):
            table_elements[v.word_id].append("{:.4f}".format(v.value))
    """

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable", classes= "responsive-table")

    return render_template('topic.html', title = "Topico #" + str(topic_id),
        ts_id = tset.id, topic_id= topic_id, nwords = t.nwords, table = table)

@app.route("/ts<int:ts_id>/word/<int:word_id>")
def word(ts_id, word_id):
    w = Word.query.filter_by(id=word_id).one() # Para asegurar primero que la palabra exista
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    topics_associations = TopicWordAssociation.query\
        .filter_by(topicset_id = ts_id)\
        .filter_by(word_id = w.id)\
        .all()

    return render_template('word.html', title = w.word_string, ts_id = tset.id, word = w, topics_associations = topics_associations)

@app.route("/ts<int:ts_id>/vocabulary")
def vocabulary(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    page = request.args.get('page', 1, type=int)
    results = WordTopicsNumber.query\
        .filter_by(topicset_id = tset.id)\
        .order_by(WordTopicsNumber.word_id)\
        .paginate(per_page = 100, page = page)

    return render_template('vocabulary.html', title= "Vocabulario", ts_id = tset.id, results = results)

@app.route("/ts<int:ts_id>/vocabulary_all")
def vocabulary_all(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    table_headings = ['ID', 'Palabra']
    table_elements = dict()
    for word in Word.query:
        table_elements[word.id] = list()
        id_link = "<a href=\"" + url_for('word', ts_id = tset.id, word_id = word.id) + "\">" \
                    + str(word.id)+ "</a>"
        table_elements[word.id].append(id_link)
        table_elements[word.id].append(word.word_string)

    table_headings.append('No. Tópicos')
    q = WordTopicsNumber.query\
        .filter_by(topicset_id = tset.id)

    for elem in q:
        table_elements[elem.word_id].append(int(elem.ntopics))

    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable", classes= "responsive-table")

    return render_template('vocabulary_all.html', title= "Vocabulario", ts_id = tset.id, wnum = len(table_elements), table = table)

"""
@app.route("/vocabulary_all")
def vocabulary_all():
    word_list = Word.query.order_by(Word.id)
    wnum = word_list.count()
    return render_template('vocabulary_all.html', title= "Vocabulario", wnum = wnum, word_list = word_list)
"""

@app.route("/ts<int:ts_id>/search", methods=['GET', 'POST'])
def search(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_result', ts_id = ts_id, searched=form.searched.data))
    return render_template("search.html", form = form, ts_id = tset.id)

@app.route("/ts<int:ts_id>/search_result")
def search_result(ts_id):
    tset = db.session.query(TopicSet).filter(TopicSet.id == ts_id).one() # para que si no existe el topicset, suceda un error
    searched = request.args.get('searched', " ", type=str)
    look_for = '%{0}%'.format(searched) # para poder hacer la busqueda "LIKE %word%"
    word_list = Word.query.filter(Word.word_string.ilike(look_for))
    return render_template('search_result.html', ts_id = tset.id, searched = searched, word_list = word_list, wlen = word_list.count())

if __name__ == '__main__':
    app.run(debug = True)
