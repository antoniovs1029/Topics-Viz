from topics_viz import db
from topics_viz.models import *
from topics_viz.models_distributions import *

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

def load_topics_set_and_distrib(file_path, topicset_name, distrib_name, topicset_description = "Empty Description", topicdistrib_description = "Empty Description", topicdistrib_normalization_value = None):
    tset = TopicSet(name = topicset_name, description = topicset_description)
    db.session.add(tset)
    db.session.commit()

    twdis = TopicWordDistribution(id = 0, topicset_id = tset.id, name = distrib_name, description = topicdistrib_description)
    db.session.add(twdis)
    db.session.commit()

    max_value = 0
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
                if word_val > max_value:
                    max_value = word_val

                # new_topic.nwords += 1 # No puedo hacer esto pues no he hecho commit del objeto
                # Word.query.filter_by(id = word_id).one().ntopics += 1 # esto tambien alenta el ciclo... me pregunto si habra alguna manera mas rapida de hacerlo!

            if i % 100 == 0:
                db.session.commit() # @TODO: No se cada cuanto hacerlo. Ya que al hacerlo mas frecuentemente si se tarda mas.

    if topicdistrib_normalization_value:
        twdis.normalization_value = topicdistrib_normalization_value
    else:
        twdis.normalization_value = max_value

    db.session.commit()


    print("Actualizando Topicos")
    cont = 0
    for t in Topic.query.filter_by(topicset_id = tset.id):
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

def load_topics_distrib(file_path, topicset_id, name, description = "Emtpy Description", normalization_value = None):
    tset = db.session.query(TopicSet).filter(TopicSet.id == topicset_id).one() # para que si no existe el topicset, suceda un error

    print("Cargando distrib", name)
    # twdis_id = db.session.query(TopicWordDistribution).filter(TopicWordDistribution.topicset_id==0).count()
    twdis_id = db.session.query(TopicWordDistribution).filter(TopicWordDistribution.topicset_id==tset.id).count() #@TODO: Cambiar esto, pues si se borra alguna distribucion, entonces esto causara colision entre los indices
    twdis = TopicWordDistribution(name = name, id = twdis_id, topicset_id = tset.id, description = description)
    db.session.add(twdis)
    db.session.commit()

    max_value = 0
    with open(file_path) as fp:
        for topic_id, line in enumerate(fp):
            for elem in line.split(" ")[1:]:
                word_id, word_val = tuple(elem.split(":"))
                word_id = int(word_id)
                word_val = float(word_val)
                new_val = TopicWordValue(topicset_id = tset.id, topic_id = topic_id, word_id = word_id, twdis_id = twdis.id, value = word_val)
                if word_val > max_value:
                    max_value = word_val

                db.session.add(new_val)

    if normalization_value:
        twdis.normalization_value = normalization_value
    else:
        twdis.normalization_value = max_value

    db.session.commit()

    # @TODO: Comprobar que la distribucion ingresada sea valida, en que las tuplas (word, topic) que usa realmente sean válidas
    # En la implementacion actual si se meten datos erroneos, no avisa... y al generar la pagina del topico, explota

def load_documents(file_path):
    print("Cargando documentos")
    with open(file_path) as fp:
        for doc_id, line in enumerate(fp):
            new_doc = Document(id = doc_id, title = line.strip('\n'))
            db.session.add(new_doc)
    db.session.commit()

def load_topic_document_distribution(file_path, topicset_id, name= "Empty Name", description = "Empty Description"):
    print("Cargado Distribución Tópico-Documento")
    tset = db.session.query(TopicSet).filter(TopicSet.id == topicset_id).one() # para que si no existe el topicset, suceda un error
    tddis_id = db.session.query(TopicDocumentDistribution).filter(TopicDocumentDistribution.topicset_id==tset.id).count()
    tddis = TopicDocumentDistribution(id = tddis_id, topicset_id = tset.id, name= name, description = description)
    db.session.add(tddis)
    with open(file_path) as fp:
        for topic_id, line in enumerate(fp):
            for elem in line.split(" ")[1:]:
                document_id, val = tuple(elem.split(":"))
                document_id = int(document_id)
                val = float(val)
                new_val = TopicDocumentValue(topicset_id = tset.id, topic_id = topic_id, document_id = document_id, tddis_id = tddis.id, value = val)
                db.session.add(new_val)
    db.session.commit()
