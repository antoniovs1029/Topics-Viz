import time

from topics_viz import app, db
from flask import render_template, url_for, redirect, request

from topics_viz.models import Topic, Word, Topic_Word_Association
from topics_viz.forms import SearchForm

@app.route("/")
def hello():
    return "Bienvenido al Topic Vizualizer"

@app.route("/topics")
def topics():
    MAX_WORDS = 5
    topic_list = []
    tnum = 0

    """
    for t in Topic.query.all():
        tnum += 1
        tlen = t.nwords
        word_list = sorted (t.words, key=lambda x: x.probability, reverse=True)
        word_list = word_list[:min(len(word_list), MAX_WORDS)]
        topic_list.append((tlen, word_list))
    """
    topic_list = Topic.query.all()

    return render_template('topics.html', title="Topicos", tnum = len(topic_list), topic_list = topic_list) 

@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    t = Topic.query.filter_by(id=topic_id).one()
    word_list = sorted (t.words, key=lambda x: x.probability, reverse=True) # lista de objetos Topic_Word_Association ordenados por probabilidad
    return render_template('topic.html', title = "Topico #" + str(topic_id), topic_id= topic_id, word_list = word_list)

@app.route("/word/<int:word_id>")
def word(word_id):
    w = Word.query.filter_by(id=word_id).one()
    return render_template('word.html', title = w.word_string, word = w)

@app.route("/vocabulary")
def vocabulary():
    word_list = Word.query.order_by(Word.id)
    wnum = word_list.count()

    return render_template('vocabulary.html', title= "Vocabulario", wnum = wnum, word_list = word_list)

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_result', searched=form.word.data))
    return render_template("search.html", form = form)

@app.route("/search_result")
def search_result():
    searched = request.args.get('searched', '', type=str)
    look_for = '%{0}%'.format(searched) # para poder hacer la busqueda "LIKE %word%"
    word_list = Word.query.filter(Word.word_string.ilike(look_for))

    return render_template('search_result.html', searched = searched, word_list = word_list, wlen = word_list.count())

if __name__ == '__main__':
    app.run(debug = True)
