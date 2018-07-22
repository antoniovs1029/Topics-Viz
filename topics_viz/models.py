"""
Aqui se definen las tablas de la base de datos, utilizando Flask-SQLAlchemy.
Solamente se modelan las clases principales, el resto se encuentra en
models_distributions.py

NOTA: al trabajar con llaves primarias compuestas, no es posible autoincrementar
el indice en SQLite, por lo que es necesario disponerla al crear un registro.
"""

from topics_viz import db

class Corpus(db.Model):
    """
    Tabla para mantener un solo registro sobre el Corpus
    """
    __tablename__ = 'corpus'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), default = "Empty Name")
    description = db.Column(db.Text, default = "Empty Description")

class TopicSet(db.Model):
    """
    Cada registro se refiere a la existencia de un conjunto de tópicos
    """
    __tablename__ = 'topic_set'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), default = "Empty Name")
    description = db.Column(db.Text, default = "Empty Description")
    ntopics = db.Column(db.Integer, default= -1) # Se debe mantener manualmente

class Topic(db.Model):
    """
    Cada registro se refiere a la existencia de un topico:
    - id: es el numero identificador del Topico
    - words: es una relacion de SQLAlchemy que devuelve una lista de python con
        todos los objetos Word de las palabras que estan en el topico
    - nwords: es el numero de palabras en el topico
    """
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    topicset_id = db.Column(db.Integer, db.ForeignKey('topic_set.id'), primary_key = True)
    words = db.relationship('TopicWordAssociation', back_populates='topic')
    nwords = db.Column(db.Integer, default=0) # Se tiene que actualizar manualmente # @TODO: ver si hay alguna manera de auto-actualizar esto

    def __repr__(self):
        return '(Topic ' + str(self.id) + ')'


class Word(db.Model):
    """
    Cada registro se refiere a la existencia de una palabra en el corpus.
    - id: es el numero identificador de la palabra
    - word_string: es la cadena de la palabra
    - ntopics: es el numero de topicos en los que aparece la palabra
    - topics: es una relacion SQLAlchemy que devuelve una lista de python con todos
        los objetos Topic de los topicos donde aparece la palabra
    """
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    word_string = db.Column(db.String(20))
    topics = db.relationship('TopicWordAssociation', back_populates='word') # Debido al diseño de la Base de Datos, esta lista contiene a todos los topicos en los que aparece la palabra, sin importar el topicset

    def __repr__(self):
        return '(Word ' + str(self.id) + ' : )'

    """
    # Aunque esto funciona igual, deja muy lento al codigo:
    def ntopics2(self):
        return len(self.topics)
    """

class TopicWordAssociation(db.Model):
    """
    Cada registro asocia un topico con cada palabra que aparece en el topico.
    Esta tabla es entonces la tabla de asociacion entre las tablas 'topic' y
    'word', para representar la relacion de muchos-a-muchos que tienen.

    - topic_id y word_id son los registros que relaciona.
    """
    __tablename__ = 'topic_word_association'
    topicset_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    word = db.relationship('Word', back_populates='topics')
    topic = db.relationship('Topic', back_populates='words')
    __table_args__ = (
        db.ForeignKeyConstraint(['topicset_id', 'topic_id'], ['topic.topicset_id', 'topic.id']), {}
        ) # Foreign Key a llave compuesta, según: https://stackoverflow.com/questions/7504753/relations-on-composite-keys-using-sqlalchemy


    def __repr__(self):
        return '(T: ' + str(self.topic_id) + ', W: ' + str(self.word_id) + ')'

class WordTopicsNumber(db.Model):
    """
    Cada registro indica a cuantos topicos se relaciona una palabra, en un TopicSet
    dado. Aunque esta operacion podria realizarse usando "count()" o "len()" en
    la tabla de TopicWordAssociation, resulta mas eficiente guardar la informacion
    de manera independiente en la BD ya que es una informacion que se consulta mucho
    en la app.

    Sin embargo, la desventaja es que esta tabla DEBE de ser mantenida manualmente.
    En caso de no actualizarse manualmente, entonces suceden errores.
    """
    __tablename__ = 'word_topics_number'
    topicset_id = db.Column(db.Integer, db.ForeignKey('topic_set.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    ntopics = db.Column(db.Integer, default=0)
    word = db.relationship('Word') # Para acceder a la palabra con la que se relaciona mas rapidamente

    def __repr__(self):
        return '(TS: ' + str(self.topicset_id) + ', W: ' + str(self.word_id) + ', Ntopics: ' + str(self.ntopics) + ')'

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))

    def __repr__(self):
        return '(Doc: ' + str(self.id) + ')'
