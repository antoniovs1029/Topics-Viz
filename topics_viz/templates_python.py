"""
Estas templates podrian hacerse en Jinja, pero considero mejor hacerlas directamente en Python, pues Jinja parece tardarse mucho cuando renderiza HTML que contienen muchas variables o loops
"""

from flask import url_for

def create_HTML_table(table_headings, table_elements, show_id = True, id_url = None):
    table = "<table>"

    # Creando los headers
    table += "<tr>"
    for elem in table_headings:
        table += "<th>" + str(elem) + "</th>"
    table+="</tr>"

    # Metiendo renglones en la tabla
    for elem_id, elem_row in table_elements.items():
        table += "<tr>"
        for elem in elem_row:
            table += "<td>" + str(elem) + "</td>"
        table += "</tr>"

    table += "</table>"
    return table