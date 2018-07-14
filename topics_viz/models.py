from topics_viz import db

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    words = db.relationship('Topic_Word_Association', back_populates='topic')
    nwords = db.Column(db.Integer, default=0) # Se tiene que actualizar manualmente # @TODO: ver si hay alguna manera de auto-actualizar esto

    def __repr__(self):
        return '(Topic ' + str(self.id) + ')'


class Word(db.Model):
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
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    probability = db.Column(db.Float, nullable=False)
    word = db.relationship('Word', back_populates='topics')
    topic = db.relationship('Topic', back_populates='words')