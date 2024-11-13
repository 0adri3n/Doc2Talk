from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ClearForm(FlaskForm):
    submit = SubmitField("Clear history")
