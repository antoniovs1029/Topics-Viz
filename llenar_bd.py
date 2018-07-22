"""
Para meter datos en la BD a partir de los archivos en la carpeta
"datos_prueba"
"""

from topics_viz import db
from topics_viz.models import *
from topics_viz.load_files import info_corpus, load_word_list, load_topics_set_and_distrib, load_topics_distrib
from topics_viz.db_utils import clear_data

clear_data()
info_corpus("NIPS", "Es el corpus del NIPS")
print("Cargando palabras")
load_word_list("./datos_prueba/word_list.txt")
print("Cargando Distribuciones")
load_topics_set_and_distrib("./datos_prueba/ts1_distrib1.txt", "Set 1", "Distrib 1")
load_topics_distrib("./datos_prueba/ts1_distrib2.txt", 1, "Distrib 2")
load_topics_distrib("./datos_prueba/ts1_distrib3.txt", 1, "SMH Index")

"""
load_topics_set_and_distrib("./datos_prueba/ts2_distrib1.txt", "Topic Set 2", "SMH Index", "r = 4")
load_topics_set_and_distrib("./datos_prueba/ts3_distrib1.txt", "Topic Set 3", "SMH Index", "r = 5")
"""
