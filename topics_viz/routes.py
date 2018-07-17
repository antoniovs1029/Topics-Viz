import time

from topics_viz import app, db
from flask import render_template, url_for, redirect, request

from topics_viz.models import Topic, Word, Topic_Word_Association, Topic_Distribution, Probability
from topics_viz.forms import SearchForm
from topics_viz.templates_python import create_HTML_table


@app.route("/")
@app.route("/home")
def home():
    return redirect(url_for('topics'))


@app.route("/topics")
def topics():
    page = request.args.get('page', 1, type=int)
    results = Topic.query.order_by(Topic.id).paginate(per_page = 50, page = page)
    return render_template('topics.html', title="Topicos", results = results) 

@app.route("/topics_all")
def topics_all():
    topic_list = Topic.query.all()
    return render_template('topics_all.html', title="Topicos", tnum = len(topic_list), topic_list = topic_list) 

"""
@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    t = Topic.query.filter_by(id=topic_id).one()
    word_list = sorted (t.words, key=lambda x: x.probability, reverse=True) # lista de objetos Topic_Word_Association ordenados por probabilidad
    return render_template('topic.html', title = "Topico #" + str(topic_id), topic_id= topic_id, word_list = word_list)
"""

@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    t = Topic.query.filter_by(id=topic_id).one()

    table_elements = dict()
    table_headings = ['ID', 'Palabra', 'No. Tópicos']
    for word_assoc in t.words:
        table_elements[word_assoc.word.id] = list()
        id_link = "<a href=\"" + url_for('word', word_id = word_assoc.word.id) + "\">" \
                    + str(word_assoc.word.id)+ "</a>"
        table_elements[word_assoc.word.id].append(id_link)
        table_elements[word_assoc.word.id].append(word_assoc.word.word_string)
        table_elements[word_assoc.word.id].append(word_assoc.word.ntopics)

    for tdis in Topic_Distribution.query.all():
        table_headings.append(tdis.name)
        for prob in Probability.query.filter_by(tdis_id = tdis.id, topic_id = topic_id).all():
            table_elements[prob.word_id].append("{:.4f}".format(prob.probability))


    table = create_HTML_table(table_headings, table_elements, id_attr = "myTable", classes= "responsive-table")

    return render_template('topic.html', title = "Topico #" + str(topic_id), topic_id= topic_id, 
        nwords = t.nwords, table = table)

@app.route("/word/<int:word_id>")
def word(word_id):
    w = Word.query.filter_by(id=word_id).one()
    return render_template('word.html', title = w.word_string, word = w)

@app.route("/vocabulary")
def vocabulary():
    page = request.args.get('page', 1, type=int)
    results = Word.query.order_by(Word.id).paginate(per_page = 100, page = page)
    return render_template('vocabulary.html', title= "Vocabulario", results = results)

@app.route("/vocabulary_all")
def vocabulary_all():
    word_list = Word.query.order_by(Word.id)
    wnum = word_list.count()
    return render_template('vocabulary_all.html', title= "Vocabulario", wnum = wnum, word_list = word_list)

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_result', searched=form.searched.data))
    return render_template("search.html", form = form)

@app.route("/search_result")
def search_result():
    searched = request.args.get('searched', " ", type=str)
    look_for = '%{0}%'.format(searched) # para poder hacer la busqueda "LIKE %word%"
    word_list = Word.query.filter(Word.word_string.ilike(look_for))
    return render_template('search_result.html', searched = searched, word_list = word_list, wlen = word_list.count())

@app.route("/ts<int:ts_id>/p")
def p(ts_id):
    """
    Esto es solo para hacer pruebas ocasionales, mientras hago el desarrollo
    """
    v = "<table style=''><tr><th>+" + str(ts_id) + "</th><th>Dos</th></tr><tr><td>1</td><td>2</td></tr></table>"
    return render_template('p.html', v = v)

if __name__ == '__main__':
    app.run(debug = True)
