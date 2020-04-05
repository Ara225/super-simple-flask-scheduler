'''
## app.py: App main entry point 
### Purpose
* Initialize the scheduler and Flask app
* Add routes to the app
* Functions for serving those routes

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
from SSHclient import Client
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
    jobs = json.loads(get_jobs().get_data().decode('utf-8'))
    return render_template('MainPageTemplate.html', JobResultsList=JobResultsList, PendingJobs=jobs, shouldShowHeader=False)

def addJob():
    '''
    Add new jobs using Flask APScheduler 
    :returns: rendered template AddJobPageTemplate.html
    '''
    try:
        # Generate secret key. Required by wtforms Doesn't store really so works only if you don't mess with the page
        letters = string.ascii_letters + string.digits
        app.config['SECRET_KEY'] =  ''.join(random.choice(letters) for i in range(60))
        # Instate the form object
        form = AddJobForm(request.form)
        
        # If this is a post request
        if request.method == 'POST':
            global JobResultsList
            #### Shell jobs 
            if form.validate() and request.form.get('targetHost', '') == '':
                if request.form.get('targetHostUser', '') != '' or request.form.get('targetHostPassword', '') != '':
                    flash('Error: Target host not supplied')
                else:
                    client = None
                    jobType = 'Shell'
                    #### One off job at specific time
                    if request.form.get('DateTimeField', '') != '' :
                        scheduleOneOffJob(jobType, request, scheduler, JobResultsList, client)
                    else:
                        #### Repeating job at specified intervals
                        success = scheduleRepeatingJob(jobType, request, scheduler, JobResultsList, client)
                        #### Fallback - run job now
                        if not success:
                            runJobNow(jobType, request, scheduler, JobResultsList, client)
            # If the target host field is completed
            elif form.validate() and request.form.get('targetHost', '') != '':
                # Target host user
                if request.form.get('targetHostUser', '') == '':
                    flash('Error: Target host user not provided')
                # If none of the password/credential fields is completed
                elif request.form.get('targetHostPassword', '') == '' and request.form.get('targetHostSSHKey', '') == '' and request.form.get('shouldUseExistingSSHKey', '') == '':
                    flash('Error: Neither password or SSH key provided')
                else: 
                    # Instigate the client object to do SSH
                    client = Client(request)
                    if client.test_connection() != False:
                        jobType = 'Remote'
                        #### One off job at specific time
                        if request.form.get('DateTimeField', '') != '' :
                            scheduleOneOffJob(jobType, request, scheduler, JobResultsList, client)
                        else:
                            #### Repeating job at specified intervals
                            success = scheduleRepeatingJob(jobType, request, scheduler, JobResultsList, client)
                            #### Fallback - run job now
                            if not success:
                                runJobNow(jobType, request, scheduler, JobResultsList, client)
            #### Failed validation
            elif not form.validate(): 
                flash('Error: Required form fields empty')
            #### Other errors
            else:
                flash('Error: Unknown issue occurred')
    except Exception as e:
        flash('Error: Unable to schedule task due to unexpected error ' + str(e))
    return render_template('AddJobPageTemplate.html')

def getJobs():
    '''
    Get Jobs using one of Flask APScheduler's job APIs (get_jobs)
    :returns: rendered template ViewJobsPageTemplate.html
    '''

    jobs = json.loads(get_jobs().get_data().decode('utf-8'))

    return render_template('ViewJobsPageTemplate.html', jobs=jobs, shouldShowHeader=True) 

def getJobsResults():
    '''
    Render job results nicely
    :returns: rendered template JobsResultPageTemplate.html
    '''
    return render_template('JobsResultPageTemplate.html', jobs=JobResultsList, wasCleaned=wasCleaned, shouldShowHeader=True) 

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
    app.run(host='0.0.0.0', debug=True) #, ssl_context='adhoc'