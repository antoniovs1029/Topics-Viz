"""
Para meter datos en la BD a partir de los archivos en la carpeta
"datos_prueba"
"""

from topics_viz import db
from topics_viz.models import *
from topics_viz.load_files import (info_corpus, load_word_list,
    load_topics_set_and_distrib, load_topics_distrib, load_documents,
    load_topic_document_distribution)
from topics_viz.db_utils import clear_data


clear_data()
info_corpus("NIPS", "Es el corpus del NIPS")
print("Cargando palabras")
load_word_list("./datos_prueba/word_list.txt")
print("Cargando Distribuciones")

smhindex_description = "El SMH Index es el numero de colisiones que tuvo la palabra en el proceso aglomerativo que formó al tópico a través del método de SampleMinHashing."

load_topics_set_and_distrib("./datos_prueba/ts1_distrib3.txt", "SMH R3", "SMH Index",
    topicset_description="Tópicos obtenidos corriendo el SMH con r = 3", topicdistrib_description = smhindex_description)
load_topics_distrib("./datos_prueba/ts1_distrib1.txt", 1, "Metodo 1", description = "Distribucion de probabilidad utilizando el 'metodo 1' propuesto, que consistia simplemente en obtener el cociente entre la frecuencia de la palabra en el corpus y la suma de las frecuencias de las palabras en el topico")
load_topics_distrib("./datos_prueba/ts1_distrib2.txt", 1, "Metodo 2 (c=50%)", description= "Distribucion de probabilidad utilizando el 'metodo 2' propuesto, usando un cutoff del 50%. Esto significa que se tomaron los documentos del corpus en donde aparecía al menos el 50% del vocabulario de un tópico dado, y luego se calculaban las frecuencias apartir de ahí para obtener el mismo cociente que el método uno (pero considerando el subconjunto del corpus obtenido con el cutoff). Debido a que en muchos casos, no había documentos que tuvieran más del 50% de las palabras de un tópico, entonces en muchos tópicos se considera que las palabras no tienen frecuencia, y por tanto tienen probabilidad 0.")

load_documents("./datos_prueba/nips.docs.txt")
load_topic_document_distribution("./datos_prueba/tdfile1.txt", 1,  name= "Palabras del Topico", description = "En esta distribución se indica cuántas palabras de cada tópico aparecen en cada documento. Si la cantidad es '0', entonces se omite la asociación.")

load_topics_set_and_distrib("./datos_prueba/ts2_distrib1.txt", "SMH R4", "SMH Index",
    topicset_description="Tópicos obtenidos corriendo el SMH con r = 4", topicdistrib_description = smhindex_description)
load_topics_set_and_distrib("./datos_prueba/ts3_distrib1.txt", "SMH R5", "SMH Index",
    topicset_description="Tópicos obtenidos corriendo el SMH con r = 5", topicdistrib_description = smhindex_description)
