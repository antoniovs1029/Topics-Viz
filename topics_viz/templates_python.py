"""
Estas templates podrian hacerse en Jinja, pero considero mejor hacerlas directamente en Python, pues Jinja parece tardarse mucho cuando renderiza HTML que contienen muchas variables o loops
"""

from flask import url_for

def create_HTML_table(table_headings, table_elements, styles = None, classes = None, id_attr = None):
    # Apertura del tag <table>
    table = "<table"
    if classes:
        table += " class=\"" + classes + "\""
    if styles:
        table += " style=\"" + styles + "\""
    if id_attr:
        table += " id=\"" + id_attr + "\""
    
    table += ">"

    # Creando los headers
    table += "<thead>"
    table += "<tr>"
    for elem in table_headings:
        table += "<th>" + str(elem) + "</th>"
    table+="</tr>"
    table += "</thead>"

    # Metiendo renglones en la tabla
    table += "<tbody>"
    for elem_id, elem_row in table_elements.items():
        table += "<tr>"
        for elem in elem_row:
            table += "<td>" + str(elem) + "</td>"
        table += "</tr>"
    table += "</tbody>"

    table += "</table>"
    return table