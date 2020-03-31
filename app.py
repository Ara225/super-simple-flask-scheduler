'''
## app.py: App main entry point 

### Imports:
#### Standard Library
* datetime
* random
* string
* sleep from time
* json
* match from re
* os
##### Internal
* jobs - Definition of the diffrent job types and the JobResults class to contain results
* forms - Definition of various forms used
##### Other
* flask - Basic web front end functionality
* flask_apscheduler - scheduler functionality intergrated with Flask
* flask_apscheduler.api get_jobs - Return jobs objects in Json

### Purpose
* Initialize the scheduler and Flask app
* Add routes to the app

### Routes
* / -> index() | Supports: GET
* /getjobs -> getJobs() | Supports: GET
* /getjobsresults -> getJobsResults() | Supports: GET
* /addjob -> addJob() | Supports: GET POST
'''
from flask import Flask, redirect, url_for, render_template, request, flash
from flask_apscheduler import APScheduler
from flask_apscheduler.api import get_jobs
from datetime import datetime
import random
import string
from time import sleep
import json
from jobs import *
from forms import *
from re import match
import os

app = None
scheduler = None
JobResultsList = []
wasCleaned = False

class Config(object):
    '''
    Config for the Flask APScheduler. If you want the API enabled set SCHEDULER_API_ENABLED to True 
    '''
    JOBS = [
        {'id': 'CleanupJob',
         'func': '__main__:CleanupJob', 
         'trigger':'interval', 
         'hours': 1
        }
    ]
    SCHEDULER_API_ENABLED = False

def index(): 
    '''
    Main page 
    :returns: rendered template MainPageTemplate.html
    '''   
    return render_template('MainPageTemplate.html')

def addJob():
    '''
    Add new jobs using Flask APScheduler 
    :returns: rendered template AddJobPageTemplate.html
    ## Uses
    AddJobForm() - form for the add job screen, defined in forms.py
    runShellCommandJob() - to run shell commands, defined in jobs.py 
    #TODO Need more job types, actual scheduling
    '''
    # Generate secret key. Required by wtforms Doesn't store really so works only if you don't mess with the page
    letters = string.ascii_letters + string.digits
    app.config['SECRET_KEY'] =  ''.join(random.choice(letters) for i in range(60))
    # Instate the form object
    form = AddJobForm(request.form)
    
    # If this is a post request
    if request.method == 'POST':
        global JobResultsList
        if form.validate() and request.form['typeSelector'] == 'Shell Job':
            if request.form.get('DateTimeField', '') != '' :
                # Get a date time object out of the input
                whenToRun = datetime.fromisoformat(request.form['DateTimeField'])
                difference = whenToRun - datetime.now()
                # This checks if the date given is in the past. The days will be at least -1 if so
                if difference.days > 0:
                    # Schedule a shell job, args are passed to the function not shell command
                    scheduler.add_job(request.form['jobId'], '__main__:runShellCommandJob', 
                                     args=(request.form['command'], request.form['jobId'], JobResultsList), 
                                     trigger='date', run_date=whenToRun)
                    flash('Shell job scheduled for ' + str(whenToRun))
                else:
                    flash('Error: Past date selected, please try again')
            else:
                intervalFieldsHaveValue = None
                # These can be returned even if they have nothing or only whitespace in them so we need to do some processing
                intervalFields = [request.form.get('Seconds', ''), request.form.get('Minutes', ''), request.form.get('Hours', ''), 
                            request.form.get('Days', ''), request.form.get('Weeks', '')]
                # These fields come out as strings so need to do some processing to make them work
                count = 0
                for i in intervalFields:
                    # If field isn't blank
                    if i != '' and i.replace(' ', '') != '' and i != None:
                        # If it's made up entirely of numbers. We have client side validation (pattern field in text fields) 
                        # but there's no point in not being careful
                        if match(r'^[0-9]*$', i):
                            intervalFieldsHaveValue = True
                            intervalFields[count] = int(i)
                        else:
                            flash('Error: Invalid input - non-number chars in interval field')
                    else:
                        intervalFields[count] = 0
                    count += 1
                if intervalFieldsHaveValue == True:
                    # Validate that the seconds, hours and minutes are less than 60
                    if intervalFields[0] >= 60 or intervalFields[1] >= 60 or intervalFields[2] >= 60:
                        flash('Error: Invalid input - second, hour or minute interval field contains a value equal to or over sixty')
                    else:
                        schedulerEnd = request.form.get('EndDateTimeField', None)
                        schedulerStart = request.form.get('StartDateTimeField', None)
                        if schedulerStart == '':
                            schedulerStart = None
                        if schedulerEnd == '':
                            schedulerEnd = None  
                        # Schedule a shell job to run at the requested interval, args are passed to the function not shell command
                        scheduler.add_job(request.form['jobId'], '__main__:runShellCommandJob', 
                                         args=(request.form['command'], request.form['jobId'], JobResultsList), 
                                         trigger='interval', seconds=intervalFields[0], minutes=intervalFields[1], 
                                         hours=intervalFields[2], days=intervalFields[3], weeks=intervalFields[4], 
                                         start_date=schedulerStart, end_date=schedulerEnd)
                        # This causes this to be displayed on the screen under the form
                        flash('Shell job scheduled to run at interval')
                else:
                    # Schedule a shell job now, args are passed to the function not shell command
                    scheduler.add_job(request.form['jobId'], '__main__:runShellCommandJob', 
                                     args=(request.form['command'], request.form['jobId'], JobResultsList), 
                                     trigger='date', run_date=datetime.now())
                    # This causes this to be displayed on the screen under the form
                    flash('Shell job scheduled for now')
                
        # Python job type 
        elif form.validate() and request.form['typeSelector'] == 'Python Job':
            flash('Error: Not yet implemented')
        
        # This causes this error to be displayed on the screen under the form if the form doesn't validate
        elif not form.validate(): 
            flash('Error: Required Form Fields Empty')
        
        # Other errors
        else:
            flash('Error: Unknown issue occurred')
    
    return render_template('AddJobPageTemplate.html')

def getJobs():
    '''
    Get Jobs using one of Flask APScheduler's job APIs (get_jobs)
    :returns: rendered template ViewJobsPageTemplate.html
    #TODO Make this look nice
    '''

    jobs = json.loads(get_jobs().get_data().decode('utf-8'))

    return render_template('ViewJobsPageTemplate.html', jobs=jobs) 

def getJobsResults():
    '''
    Render job results nicely
    :returns: rendered template JobsResultPageTemplate.html
    '''
    return render_template('JobsResultPageTemplate.html', jobs=JobResultsList, wasCleaned=wasCleaned) 

def CleanupJob():
    '''
    Function to clean up JobResultsList to prevent it from getting too big 
    TODO improve functionality
    '''
    global JobResultsList
    if len(JobResultsList) > 100:
        with open('JobResultsDump.txt', 'w') as f:
            f.writelines(JobResultsList)
        JobResultsList = []
        global wasCleaned 
        wasCleaned = True
    

def runApp():
    '''
    Run the app: start app, scheduler, add routes
    '''
    # Instigate app
    global app 
    app = Flask(__name__)
    # Add config to app
    app.config.from_object(Config())
    # Start scheduler
    global scheduler 
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    # Add routes
    app.add_url_rule("/", "/", index, methods=['GET'])
    app.add_url_rule("/getjobs", "/getjobs", getJobs, methods=['GET'])
    app.add_url_rule("/getjobsresults", "/getjobsresults", getJobsResults, methods=['GET'])
    app.add_url_rule("/addjob", "/addjob", addJob, methods=['GET', 'POST'])
    return app

if __name__ == '__main__': 
    runApp()        
    app.run(host='0.0.0.0', debug=True)