"""
Funciones para manejar la Base de Datos
"""

from topics_viz.models import *

def delete_Topic_Word_Distribution(id):
    db.session.query(Topic_Word_Distribution).filter(TopicWordDistribution.id).delete() # Eliminar de tabla Topic_Word_Distribution
    db.session.query(TopicWordValue).filter(TopicWordValue.tdis_id = 1).delete() # Eliminar de tabla TopicWordValue
    db.session.commit()
