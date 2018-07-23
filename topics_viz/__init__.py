from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c67dfde280ba245'

db = SQLAlchemy(app)

from topics_viz import routes
from topics_viz import routes_plots
from topics_viz import routes_distributions
from topics_viz import routes_exploration