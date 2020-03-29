'''
Forms.py: Functions and classes related to jobs
'''
from wtforms import Form, TextField, validators, SubmitField, SelectField, RadioField, ValidationError
from pprint import pprint

class AddJobForm(Form):
    '''
    Form for the add jobs page. This contains a number of fields:
    * jobId field - TextField type - Job name/ID - validator for this is simply that data is required
    * command field - TextField type - Command to run - validator for this is simply that data is required
    * typeSelector field - SelectField type - Select the job type (Shell, Python) - validator is that the '' field is not selected
    '''
    jobId = TextField('jobId', validators=[validators.DataRequired()])
    command = TextField('command', validators=[validators.DataRequired()])
    typeSelector = SelectField('typeSelector', 
                   validators=[validators.none_of([('-- Select Job Type --', '-- Select Job Type --')])], 
                   choices=[('-- Select Job Type --', '-- Select Job Type --'), ('Python Job', 'Python Job'), ('Shell Job', 'Shell Job')]
                   )
    timeField = TextField('timeField', validators=[validators.optional(strip_whitespace=True)])
    dateField = TextField('dateField', validators=[validators.optional(strip_whitespace=True)])

    seconds = TextField('Seconds', validators=[validators.optional(strip_whitespace=True)])
    minutes = TextField('Minutes', validators=[validators.optional(strip_whitespace=True)])
    hours = TextField('Hours', validators=[validators.optional(strip_whitespace=True)])
    days = TextField('Days', validators=[validators.optional(strip_whitespace=True)])
    weeks = TextField('Weeks', validators=[validators.optional(strip_whitespace=True)])

