from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    searched = StringField('Busca Cadena', validators = [DataRequired()])
    submit = SubmitField('Buscar')