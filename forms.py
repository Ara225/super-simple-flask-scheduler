'''
Forms.py: Functions and classes related to backend stuff for forms. Only contains the form for 
the add jobs page currently
'''
from wtforms import Form, StringField, validators, SubmitField, SelectField, RadioField, ValidationError
from pprint import pprint

class AddJobForm(Form):
    '''
    Form for the add jobs page. This contains a number of fields:
    * jobId field - StringField type - Job name/ID - validator for this is simply that data is required
    * command field - StringField type - Command to run - validator for this is simply that data is required
    * typeSelector field - SelectField type - Select the job type (Shell, Python) - validator is that the '-- Select Job Type --' field is not selected
    * dateTimeField - StringField type for wtforms, datetime-local type in HTML - time & date to run job 
    * seconds/minutes/hours/days/weeks - StringField type - attributes for the interval trigger type for APScheduler
    * endDateTimeField - StringField type for wtforms, datetime-local type in HTML - time to stop doing the scheduled task
    * startDateTimeField - StringField type for wtforms, datetime-local type in HTML - time to start doing the scheduled task
    '''
    # Required fields
    jobId = StringField('jobId', validators=[validators.DataRequired()])
    command = StringField('command', validators=[validators.DataRequired()])

    # Target Host 
    targetHost = StringField('targetHost', validators=[validators.optional()])
    targetHostUser = StringField('targetHostUser', validators=[validators.optional()])
    targetHostPassword = StringField('targetHostPassword', validators=[validators.optional()])
    targetHostPassphrase = StringField('targetHostPassphrase', validators=[validators.optional()])
    targetHostSSHKey = StringField('targetHostSSHKey', validators=[validators.optional()])

    # Date/time scheduler options
    dateTimeField = StringField('DateTimeField', validators=[validators.optional(strip_whitespace=True)])

    # Interval scheduler options
    seconds = StringField('Seconds', validators=[validators.optional(strip_whitespace=True)])
    minutes = StringField('Minutes', validators=[validators.optional(strip_whitespace=True)])
    hours = StringField('Hours', validators=[validators.optional(strip_whitespace=True)])
    days = StringField('Days', validators=[validators.optional(strip_whitespace=True)])
    weeks = StringField('Weeks', validators=[validators.optional(strip_whitespace=True)])
    startDateTimeField = StringField('StartDateTimeField', validators=[validators.optional(strip_whitespace=True)])
    endDateTimeField = StringField('EndDateTimeField', validators=[validators.optional(strip_whitespace=True)])