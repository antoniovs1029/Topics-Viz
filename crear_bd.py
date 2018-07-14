from topics_viz import db
db.reflect()
db.drop_all()

from topics_viz.models import Topic, Word, Topic_Word_Association

db.create_all()