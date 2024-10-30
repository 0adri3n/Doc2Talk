from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class QuestionForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired(), Length(min=5, max=400)])
    submit = SubmitField('Poser la question')
