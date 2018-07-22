from topics_viz import db
from topics_viz.models import *

from sqlalchemy import func

def info_corpus(name, description):
    c = Corpus(name = name, description = description)
    db.session.add(c)
    db.session.commit()

def load_word_list(file_path):
    with open(file_path, 'r') as fp:
        for i, word in enumerate(fp):
            word = word.split(" ")[0].strip('\n')
            new_word = Word(id = i, word_string = word)
            db.session.add(new_word)
        db.session.commit()

def load_topics_set_and_distrib(file_path, topicset_name, distrib_name, topicset_description = "Empty Description", topicdistrib_description = "Empty Description"):
    tset = TopicSet(name = topicset_name)
    db.session.add(tset)
    db.session.commit()

    twdis = TopicWordDistribution(id = 0, topicset_id = tset.id, name = distrib_name)
    db.session.add(twdis)
    db.session.commit()

    with open(file_path, 'r') as fp:
        for i, line in enumerate(fp):
            print("Cargando topico: ", i)
            new_topic = Topic(topicset_id = tset.id, id = i)
            db.session.add(new_topic)

            for elem in line.split(" ")[1:]:
                word_id, word_val = tuple(elem.split(":"))
                word_id = int(word_id)
                word_val = float(word_val)
                new_assoc = TopicWordAssociation(topicset_id = tset.id, topic_id = i, word_id = word_id)
                new_val = TopicWordValue(topicset_id = tset.id, topic_id = i, word_id = word_id, twdis_id = twdis.id, value = word_val)
                db.session.add(new_assoc)
                db.session.add(new_val)

                # new_topic.nwords += 1 # No puedo hacer esto pues no he hecho commit del objeto
                # Word.query.filter_by(id = word_id).one().ntopics += 1 # esto tambien alenta el ciclo... me pregunto si habra alguna manera mas rapida de hacerlo!

            if i % 100 == 0:
                db.session.commit() # @TODO: No se cada cuanto hacerlo. Ya que al hacerlo mas frecuentemente si se tarda mas.

    print("Actualizando Topicos")
    cont = 0
    for t in Topic.query.all():
        t.nwords = len(t.words)
        cont += 1

    tset.ntopics = cont

    print("Actualizando contador de topicos en las Palabras") # @TODO: Se tarda demasiado aqui
    _count_topics_for_words(tset.id)
    """
    for w in Word.query.all():
        w.ntopics = len(w.topics)

    db.session.commit()
    """
def _count_topics_for_words(topicset_id):
    for i, w in enumerate(Word.query):
        tnum = db.session.query(func.count(TopicWordAssociation.word_id))\
            .filter(TopicWordAssociation.topicset_id == topicset_id)\
            .filter(TopicWordAssociation.word_id == w.id)\
            .one()

        v = WordTopicsNumber(
            topicset_id = topicset_id,
            word_id = w.id,
            ntopics = tnum[0]
            )

        if i % 100 == 0:
            print("Procesando palabras con ID del", i, "al", i + 99)
        db.session.add(v)
    db.session.commit()
    pass

def load_topics_distrib(file_path, topicset_id, name, description = "Emtpy Description"):
    tset = db.session.query(TopicSet).filter(TopicSet.id == topicset_id).one() # para que si no existe el topicset, suceda un error

    print("Cargando distrib", name)
    # twdis_id = db.session.query(TopicWordDistribution).filter(TopicWordDistribution.topicset_id==0).count()
    twdis_id = db.session.query(TopicWordDistribution).filter(TopicWordDistribution.topicset_id==tset.id).count()
    twdis = TopicWordDistribution(name = name, id = twdis_id, topicset_id = tset.id)
    db.session.add(twdis)
    db.session.commit()

    with open(file_path) as fp:
        for topic_id, line in enumerate(fp):
            for elem in line.split(" ")[1:]:
                word_id, word_val = tuple(elem.split(":"))
                word_id = int(word_id)
                word_val = float(word_val)
                new_val = TopicWordValue(topicset_id = tset.id, topic_id = topic_id, word_id = word_id, twdis_id = twdis.id, value = word_val)
                db.session.add(new_val)
    db.session.commit()

    # @TODO: Comprobar que la distribucion ingresada sea valida, en que las tuplas (word, topic) que usa realmente sean válidas
    # En la implementacion actual si se meten datos erroneos, no avisa... y al generar la pagina del topico, explota
