from topics_viz import db
from topics_viz.models import (Word, Topic, Topic_Word_Association,
                                    Topic_Distribution, Probability)

def load_word_list(file_path):
    with open(file_path, 'r') as fp:
        for i, word in enumerate(fp):
            word = word.split(" ")[0].strip('\n')
            new_word = Word(id = i, word_string = word)
            db.session.add(new_word)
        db.session.commit()

def load_first_topics_distrib(file_path):
    tdis = Topic_Distribution()
    db.session.add(tdis)
    db.session.commit()

    with open(file_path, 'r') as fp:
        for i, line in enumerate(fp):
            print("Cargando topico: ", i)
            new_topic = Topic(id = i)
            db.session.add(new_topic)

            for elem in line.split(" ")[1:]:
                word_id, word_prob = tuple(elem.split(":"))
                word_id = int(word_id)
                word_prob = float(word_prob)
                new_assoc = Topic_Word_Association(topic_id = i, word_id = word_id)
                new_prob = Probability(topic_id = i, word_id = word_id, tdis_id = tdis.id, probability = word_prob)
                db.session.add(new_assoc)
                db.session.add(new_prob)

                # new_topic.nwords += 1 # No puedo hacer esto pues no he hecho commit del objeto
                # Word.query.filter_by(id = word_id).one().ntopics += 1 # esto tambien alenta el ciclo... me pregunto si habra alguna manera mas rapida de hacerlo!

    db.session.commit() # @TODO: No se si meter esto dentro del ciclo, pero al sacarlo, realiza sus operaciones demasiado rapido


    print("Actualizando Topicos")
    for t in Topic.query.all():
        t.nwords = len(t.words)

    print("Actualizando Palabras") # @TODO: Se tarda demasiado aqui
    for w in Word.query.all():
        w.ntopics = len(w.topics)

    db.session.commit()

def load_topics_distrib(file_path, name):
    tdis = Topic_Distribution(name = name)
    db.session.add(tdis)
    db.session.commit()

    with open(file_path, 'r') as fp:
        for topic_id, line in enumerate(fp):
            for elem in line.split(" ")[1:]:
                word_id, word_prob = tuple(elem.split(":"))
                word_id = int(word_id)
                word_prob = float(word_prob)
                new_prob = Probability(topic_id = topic_id, word_id = word_id, tdis_id = tdis.id, probability = word_prob)
                db.session.add(new_prob)

    db.session.commit()

    # @TODO: Comprobar que la distribucion ingresada sea valida, en que las tuplas (word, topic) que usa realmente sean válidas
    # En la implementacion actual si se meten datos erroneos, no avisa... y al generar la pagina del topico, explota
    
def clear_data(session = db.session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print( 'Clear table %s' % table)
        session.execute(table.delete())
    session.commit()