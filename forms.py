'''
Forms.py: Functions and classes related to backend stuff for forms. Only contains the form for 
the add jobs page currently
'''
from wtforms import Form, TextField, validators, SubmitField, SelectField, RadioField, ValidationError
from pprint import pprint

class AddJobForm(Form):
    '''
    Form for the add jobs page. This contains a number of fields:
    * jobId field - TextField type - Job name/ID - validator for this is simply that data is required
    * command field - TextField type - Command to run - validator for this is simply that data is required
    * typeSelector field - SelectField type - Select the job type (Shell, Python) - validator is that the '-- Select Job Type --' field is not selected
    * dateTimeField - TextField type for wtforms, datetime-local type in HTML - time & date to run job 
    * seconds/minutes/hours/days/weeks - TextField type - attributes for the interval trigger type for APScheduler
    * endDateTimeField - TextField type for wtforms, datetime-local type in HTML - time to stop doing the scheduled task
    * startDateTimeField - TextField type for wtforms, datetime-local type in HTML - time to start doing the scheduled task
    '''
    # Required fields
    jobId = TextField('jobId', validators=[validators.DataRequired()])
    command = TextField('command', validators=[validators.DataRequired()])
    typeSelector = SelectField('typeSelector', 
                   validators=[validators.none_of([('-- Select Job Type --', '-- Select Job Type --')])], 
                   choices=[('-- Select Job Type --', '-- Select Job Type --'), ('Python Job', 'Python Job'), ('Shell Job', 'Shell Job')]
                   )
    # Date/time scheduler options
    dateTimeField = TextField('DateTimeField', validators=[validators.optional(strip_whitespace=True)])

    # Interval scheduler options
    seconds = TextField('Seconds', validators=[validators.optional(strip_whitespace=True)])
    minutes = TextField('Minutes', validators=[validators.optional(strip_whitespace=True)])
    hours = TextField('Hours', validators=[validators.optional(strip_whitespace=True)])
    days = TextField('Days', validators=[validators.optional(strip_whitespace=True)])
    weeks = TextField('Weeks', validators=[validators.optional(strip_whitespace=True)])
    startDateTimeField = TextField('StartDateTimeField', validators=[validators.optional(strip_whitespace=True)])
    endDateTimeField = TextField('EndDateTimeField', validators=[validators.optional(strip_whitespace=True)])



