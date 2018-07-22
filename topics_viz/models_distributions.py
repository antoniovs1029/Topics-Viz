from topics_viz import db

class TopicWordDistribution(db.Model):
    """
    Cada registro se refiere a una relacion Topico-Palabra que haya sido
    dispuesta por el usuario. Por ejemplo, cada registro puede significar
    la existencia de una distribución de probabilidad dentro de la Base de
    Datos. Sin embargo no es necesario que la distribucion sea de probabilidad.

    - id: el numero identificador de la distribución Topico-Palabra
    - name: nombre de la distribución
    - description: texto que describa la distribución
    - normalization_value: número con el cual dividir para normalizar los
    valores de la distribución. Útil para graficar.

    Dentro del codigo se usa frecuentemente la abreviación "twdis" o "TWDis"
    para referirse a esta clase.
    """
    __tablename__ = 'topic_word_distribution'
    id = db.Column(db.Integer, primary_key = True)
    topicset_id = db.Column(db.Integer, db.ForeignKey('topic_set.id'), primary_key=True)
    name = db.Column(db.String(20), default = "Empty Name")
    description = db.Column(db.Text, default = "Empty Description")
    normalization_value = db.Column(db.Integer, default = 1)

    def __repr__(self):
        return 'Topic-Word Distribution #' + str(self.id)

class TopicWordValue(db.Model):
    """
    Cada registro contiene el valor de una distribución Tópico-Palabra.
    - topic_id : topico al que pertenece el valor
    - word_id: palabra a la que pertenece el valor
    - twdis_id : distribución a la que pertenece el valor
    - value: valor del elemento

    Tipicamente el valor será una probabilidad, pero esto no es nece-
    sario.
    """
    __tablename__ = 'topic_word_value'
    topicset_id = db.Column(db.Integer, primary_key = True)
    topic_id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, primary_key=True)
    twdis_id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.Float, nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['topicset_id', 'topic_id', 'word_id'],
            ['topic_word_association.topicset_id','topic_word_association.topic_id', 'topic_word_association.word_id']
            ),
        db.ForeignKeyConstraint(
            ['topicset_id', 'twdis_id'],
            ['topic_word_distribution.topicset_id', 'topic_word_distribution.id']
            ), {}
        )
    # twa = db.relationship('TopicWordAssociation', back_populates='probabilities')

    def __repr__(self):
        return '(TWDis: ' + str(self.twdis_id) + ', T: ' + str(self.topic_id) + ', W: ' + str(self.word_id) + ', V: ' + str(self.value) + ')'

class TopicDocumentDistribution(db.Model):
    __tablename__ = 'topic_document_distribution'
    id = db.Column(db.Integer, primary_key = True)
    topicset_id = db.Column(db.Integer, db.ForeignKey('topic_set.id'), primary_key=True)
    name = db.Column(db.String(20), default = "Empty Name")
    description = db.Column(db.Text, default = "Empty Description")
    normalization_value = db.Column(db.Integer, default = 1)


    def __repr__(self):
        return 'Topic-Document Distribution #' + str(self.id)

class TopicDocumentValue(db.Model):
    __tablename__ = 'topic_document_value'
    topicset_id = db.Column(db.Integer, primary_key = True)
    topic_id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, primary_key=True)
    tddis_id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.Float, nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['topicset_id', 'topic_id'],
            ['topic.topicset_id','topic.id']
            ),
        db.ForeignKeyConstraint(
            ['topicset_id', 'tddis_id'],
            ['topic_document_distribution.topicset_id', 'topic_document_distribution.id']
            ), {}
        )

    def __repr__(self):
        return '(TDDis: ' + str(self.tddis_id) + ', T: ' + str(self.topic_id) + ', D: ' + str(self.document_id) + ', V: ' + str(self.value) + ')'
