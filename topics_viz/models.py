from topics_viz import db

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    words = db.relationship('Topic_Word_Association', back_populates='topic')
    nwords = db.Column(db.Integer, default=0) # Se tiene que actualizar manualmente # @TODO: ver si hay alguna manera de auto-actualizar esto

    def __repr__(self):
        return '(Topic ' + str(self.id) + ')'


class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    word_string = db.Column(db.String(20))
    ntopics = db.Column(db.Integer, default=0) # Se tiene que actualizar manualmente # @TODO: ver si hay alguna manera de auto-actualizar esto
    topics = db.relationship('Topic_Word_Association', back_populates='word')

    def __repr__(self):
        return '(Word ' + str(self.id) + ' : )'

    """
    # Aunque esto funciona igual, deja muy lento al codigo:
    def ntopics2(self): 
        return len(self.topics)
    """

class Topic_Word_Association(db.Model):
    __tablename__ = 'twa'
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
#   probability = db.Column(db.Float, nullable=False)
    word = db.relationship('Word', back_populates='topics')
    topic = db.relationship('Topic', back_populates='words')
    # probabilities = db.relationship('Probability', back_populates='twa') 

    def __repr__(self):
        return '(T: ' + str(self.topic_id) + ', W: ' + str(self.word_id) + ')'

class Topic_Distribution(db.Model):
    __tablename__ = 'tdis'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), default = "Empty Name")
    description = db.Column(db.Text, default = "Empty Description")

    def __repr__(self):
        return 'Topic Distribution #' + str(self.id)

class Probability(db.Model):
    """
    Aunque se llama "Probability" no necesariamente tiene que ser una probabilidad
    """
    __tablename__ = 'probability'
    topic_id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, primary_key=True)
    tdis_id = db.Column(db.Integer, db.ForeignKey('tdis.id'), primary_key = True)
    __table_args__ = (db.ForeignKeyConstraint(['topic_id', 'word_id'], ['twa.topic_id', 'twa.word_id']), {}) # Foreign Key a llave compuesta, según: https://stackoverflow.com/questions/7504753/relations-on-composite-keys-using-sqlalchemy
    probability = db.Column(db.Float, nullable=False)
    # twa = db.relationship('Topic_Word_Association', back_populates='probabilities')

    def __repr__(self):
        return '(TDis: ' + str(self.tdis_id) + ', T: ' + str(self.topic_id) + ', W: ' + str(self.word_id) + ', P: ' + str(self.probability) + ')'