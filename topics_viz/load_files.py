from topics_viz import db
from topics_viz.models import Word, Topic, Topic_Word_Association

def load_word_list(file_path):
    with open(file_path, 'r') as fp:
        for i, word in enumerate(fp):
            word = word.split(" ")[0].strip('\n')
            new_word = Word(id = i, word_string = word)
            db.session.add(new_word)
        db.session.commit()

def load_topics_distrib(file_path):
    with open(file_path, 'r') as fp:
        for i, line in enumerate(fp):
            print("Cargando topico: ", i)
            new_topic = Topic(id = i)
            db.session.add(new_topic)
            db.session.commit()

            for elem in line.split(" ")[1:]:
                word_id, word_prob = tuple(elem.split(":"))
                word_id = int(word_id)
                word_prob = float(word_prob)

                new_assoc = Topic_Word_Association(topic_id = i, word_id = word_id, probability = word_prob)

                db.session.add(new_assoc)
            db.session.commit()

    print("Actualizando Topicos")
    for t in Topic.query.all():
        t.nwords = len(t.words)

    print("Actualizando Palabras") # @TODO: Se tarda demasiado aqui
    for w in Word.query.all():
        w.ntopics = len(w.topics)

    print("DB COMMIT")
    db.session.commit()


def clear_data(session = db.session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print( 'Clear table %s' % table)
        session.execute(table.delete())
    session.commit()