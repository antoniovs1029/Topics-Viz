"""
Funciones para manejar la Base de Datos
"""

from topics_viz.models import *
from topics_viz.models_distributions import *

def clear_data(session = db.session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print( 'Clear table %s' % table)
        session.execute(table.delete())
    session.commit()
