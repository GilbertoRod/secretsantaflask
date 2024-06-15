from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from secretsanta.models import User,Event

class RegisterForm(FlaskForm):

  #function that checks if a username is already existing in the database
  def validate_username(self, username_to_check):
    user=User.query.filter_by(username=username_to_check.data).first()
    if user:
      raise ValidationError('Username already exists, please try a different username')

  def validate_email_address(self, email_address_to_check):
    email_address=User.query.filter_by(email_address=email_address_to_check.data).first()
    if email_address:
      raise ValidationError('Email Address already exists, please try a different username')

  username = StringField(label='Username: ', validators=[Length(min=2,max=30), DataRequired()])
  first_name = StringField(label='First Name: ', validators=[Length(max=50), DataRequired()])
  last_name = StringField(label='Last Name: ', validators=[Length(max=50), DataRequired()])
  email_address= StringField(label='Email: ', validators=[Email(), DataRequired()])
  password1 = PasswordField(label='Password: ', validators=[Length(min=6), DataRequired()])
  password2 = PasswordField(label='Confirm Password: ', validators= [EqualTo('password1'), DataRequired()])
  submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
  username = StringField(label='Username:', validators=[DataRequired()])
  password = PasswordField(label='Password: ', validators=[DataRequired()])
  submit = SubmitField(label='Sign In')

class EventForm(FlaskForm):

  event_name = StringField(label='Event Name: ', validators=[Length(min=2,max=75), DataRequired()])
  submit = SubmitField(label='Create')
  
  
class AddUserEvent(FlaskForm):
  def validate_event_name(self, username_to_check):
    user=User.query.filter_by(username=username_to_check.data).first()
    if not user:
      raise ValidationError('User Doesn\'t exist')
  username = StringField(validators=[DataRequired()])
  submit = SubmitField(label='Add Person')
  
  
  
class FieldsForm(FlaskForm):
  field_1 = StringField(label='Entry #1:', validators=[DataRequired()])
  field_2 = StringField(label='Entry #2:')
  field_3 = StringField(label='Entry #3:')
  field_4 = StringField(label='Entry #4:')
  field_5 = StringField(label='Entry #5:')
  field_6 = StringField(label='Entry #6:')
  field_7 = StringField(label='Entry #7:')
  field_8 = StringField(label='Entry #8:')
  field_9 = StringField(label='Entry #9:')
  field_10 = StringField(label='Entry #10:')
  submit = SubmitField(label='Submit Fields')
  
class UserFieldsForm(FlaskForm):
  field_1 = StringField(validators=[DataRequired()])
  field_2 = StringField(validators=[DataRequired()])
  field_3 = StringField(validators=[DataRequired()])
  field_4 = StringField(validators=[DataRequired()])
  field_5 = StringField(validators=[DataRequired()])
  field_6 = StringField(validators=[DataRequired()])
  field_7 = StringField(validators=[DataRequired()])
  field_8 = StringField(validators=[DataRequired()])
  field_9 = StringField(validators=[DataRequired()])
  field_10 = StringField(validators=[DataRequired()])
  submit = SubmitField(label='Submit Info')

  
class UpdateUserFieldsForm(FlaskForm):
  field_1 = StringField(validators=[DataRequired()])
  field_2 = StringField(validators=[DataRequired()])
  field_3 = StringField(validators=[DataRequired()])
  field_4 = StringField(validators=[DataRequired()])
  field_5 = StringField(validators=[DataRequired()])
  field_6 = StringField(validators=[DataRequired()])
  field_7 = StringField(validators=[DataRequired()])
  field_8 = StringField(validators=[DataRequired()])
  field_9 = StringField(validators=[DataRequired()])
  field_10 = StringField(validators=[DataRequired()])
  submit = SubmitField(label='Update My Info')





