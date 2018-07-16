from topics_viz import db
db.reflect()
db.drop_all()

from topics_viz.models import *

db.create_all()