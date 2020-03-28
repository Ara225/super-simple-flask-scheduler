'''
Forms.py: Functions and classes related to jobs
'''
from wtforms import Form, TextField, validators, SubmitField, SelectField, RadioField, ValidationError
from pprint import pprint

class AddJobForm(Form):
    '''
    Form for the add jobs page. This contains three fields:
    * jobId field - TextField type - Job name/ID - validator for this is simply that data is required
    * command field - TextField type - Command to run - validator for this is simply that data is required
    * typeSelector field - SelectField type - Select the job type (Shell, Python) - validator is that the '' field is not selected
    '''
    jobId = TextField('jobId', validators=[validators.DataRequired()])
    command = TextField('command', validators=[validators.DataRequired()])
    typeSelector = SelectField('typeSelector', 
                   validators=[validators.none_of([('', '')])], 
                   choices=[('', ''), ('Python Job', 'Python Job'), ('Shell Job', 'Shell Job')]
                   )
    #scheduleType = RadioField('scheduleType', choices=[('Now','Now'), ('Later','Later')], validators=[validators.optional()])
    timeField = TextField('timeField', validators=[validators.optional()])
    dateField = TextField('dateField', validators=[validators.optional()])
