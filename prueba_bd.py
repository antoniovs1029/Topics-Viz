from topics_viz import db
from topics_viz.models import Topic, Word, Topic_Word_Association
from topics_viz.load_files import load_word_list, load_first_topics_distrib, load_topics_distrib, clear_data

"""
clear_data()
print("Cargando palabras")
load_word_list("./datos_prueba/word_list.txt")
print("Cargando Distribuciones")
load_first_topics_distrib("./datos_prueba/distrib.txt")
"""

load_topics_distrib("./datos_prueba/distrib3.txt", "SMH Index")
