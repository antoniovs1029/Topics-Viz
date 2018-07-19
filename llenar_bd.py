"""
Para meter datos en la BD a partir de los archivos en la carpeta
"datos_prueba"
"""

from topics_viz import db
from topics_viz.models import *
from topics_viz.load_files import load_word_list, load_topics_set_and_distrib, load_topics_distrib
from topics_viz.db_utils import clear_data

clear_data()
print("Cargando palabras")
load_word_list("./datos_prueba/word_list.txt")
print("Cargando Distribuciones")
load_topics_set_and_distrib("./datos_prueba/distrib.txt", "Set 1", "Distrib 1")
load_topics_distrib("./datos_prueba/distrib2.txt", 1, "Distrib 2")
load_topics_distrib("./datos_prueba/distrib3.txt", 1, "SMH Index")
