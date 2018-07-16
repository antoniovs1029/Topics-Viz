"""
Funciones para manejar la Base de Datos
"""

from topics_viz.models import *

def delete_Topic_Distribution(id):
    db.session.query(Topic_Distribution).filter(Topic_Distribution.id).delete() # Eliminar de tabla Topic_Distribution
    db.session.query(Probability).filter(Probability.tdis_id = 1).delete() # Eliminar de tabla Probability
    db.session.commit()