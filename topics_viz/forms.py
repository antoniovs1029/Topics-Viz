from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    word = StringField('Busca Palabra', validators = [DataRequired()])
    submit = SubmitField('Buscar')