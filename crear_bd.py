"""
Para eliminar las tablas existentes en la BD y crear las tablas dispuestas en
los modelos. Las nuevas tablas se encuentran vacias.
"""

from topics_viz import db
db.reflect()
db.drop_all()
db.session.commit() #Al parecer es necesario hacer commit antes del create, para que de verdad se borren las tablas

from topics_viz.models import *

db.create_all()
db.session.commit()
