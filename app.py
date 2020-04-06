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
from yaml import load, Loader
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

app = None
scheduler = None
JobResultsList = []
wasCleaned = False

class Config(object):
    '''
    Config for the Flask APScheduler. Should accept any config option valid for APScheduler - just put it in Config.yaml 
    jobstores and executors need to be in the format indicated in Config.yaml
    '''
    def __init__(self):
        self._jobstores = False
        self._executors = False
        with open('Config.yaml') as f:
            self.config = load(f, Loader=Loader)
        for item in self.config:
            # Dealing with custom jobstores and executors
            if 'jobstores' == item:
                self._jobstores = self.config[item]
                continue
            if 'executors' == item:
                self._executors = self.config[item]
                continue
            exec('self.' + item + ' = self.config["' + item + '"]')

def index(): 
    '''
    Main page 
    Displays quick summary of jobs and the contents of both the pending and completed tasks pages
    Accepts POST requests to handle deleting jobs (part of pending jobs page)
    :returns: rendered template MainPageTemplate.html
    '''   
    # Generate secret key. Required by wtforms Doesn't store really so works only if you don't mess with the page
    letters = string.ascii_letters + string.digits
    app.config['SECRET_KEY'] =  ''.join(random.choice(letters) for i in range(60))
    # Instate the form object
    form = RemoveJobForm(request.form)
    
    # If this is a post request - to handle deleting jobs
    if request.method == 'POST':
        if request.form.get('RemoveJob', '') != '':
            try:
                # Actually delete the job
                scheduler.remove_job(request.form.get('RemoveJob'))
                flash('Job successfully deleted')
            except Exception as e:
                flash('Error: Unknown issue occurred: ' + str(e))
        else:
            flash('Error: Hidden form field tampered with')

    jobs = json.loads(get_jobs().get_data().decode('utf-8'))
    return render_template('MainPageTemplate.html', JobResultsList=JobResultsList, PendingJobs=jobs, shouldShowHeader=False, wasCleaned=wasCleaned)

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
                # If the credentials fields are completed
                if request.form.get('targetHostUser', '') != '' or request.form.get('targetHostPassword', '') != '' or request.form.get('targetHostSSHKey', '') != '' or request.form.get('shouldUseExistingSSHKey', None) == 'on':
                    flash('Error: Target host not supplied')
                else:
                    client = None
                    jobType = 'Shell'
                    #### One off job at specific time
                    if request.form.get('DateTimeField', '') != '' :
                        scheduleOneOffJob(jobType, request, scheduler, JobResultsList, client)
                    elif request.form.get('ShouldUseCron', None) == 'on':
                        scheduleCronJob(jobType, request, scheduler, JobResultsList, client)
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
                elif request.form.get('targetHostPassword', '') == '' and request.form.get('targetHostSSHKey', '') == '' and request.form.get('shouldUseExistingSSHKey', None) == None:
                    flash('Error: Neither password or SSH key provided')
                else: 
                    # Instigate the client object to do SSH
                    client = Client(request)
                    if client.test_connection() != False:
                        jobType = 'Remote'
                        #### One off job at specific time
                        if request.form.get('DateTimeField', '') != '' :
                            scheduleOneOffJob(jobType, request, scheduler, JobResultsList, client)
                        elif request.form.get('ShouldUseCron', None) == 'on':
                            scheduleCronJob(jobType, request, scheduler, JobResultsList, client)
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
    # Generate secret key. Required by wtforms Doesn't store really so works only if you don't mess with the page
    letters = string.ascii_letters + string.digits
    app.config['SECRET_KEY'] =  ''.join(random.choice(letters) for i in range(60))
    # Instate the form object
    form = RemoveJobForm(request.form)
    
    # If this is a post request - to handle deleting jobs
    if request.method == 'POST':
        if request.form.get('RemoveJob', '') != '':
            try:
                scheduler.remove_job(request.form.get('RemoveJob'))
                flash('Job successfully deleted')
            except Exception as e:
                flash('Error: Unknown issue occurred: ' + str(e))
        else:
            flash('Error: Hidden form field tampered with')
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
    appconfig = Config()
    # Add config to app
    app.config.from_object(appconfig)
    # Start scheduler
    global scheduler 
    scheduler = APScheduler()
    # Add custom executors and jobstores It's kind of complicated, but the way of doing it through the Config() class won't work for this
    if appconfig._jobstores:
        for jobstore in appconfig._jobstores:
            scheduler._scheduler.add_jobstore(appconfig._jobstores[jobstore]['type'], url=appconfig._jobstores[jobstore]['url'])
    if appconfig._executors:
        for executor in appconfig._executors:
            scheduler._scheduler.add_executor(appconfig._executors[executor]['type'])
    scheduler.init_app(app)
    scheduler.start()
    # Add routes
    app.add_url_rule("/", "/", index, methods=['GET', 'POST'])
    app.add_url_rule("/getjobs", "/getjobs", getJobs, methods=['GET', 'POST'])
    app.add_url_rule("/getjobsresults", "/getjobsresults", getJobsResults, methods=['GET'])
    app.add_url_rule("/addjob", "/addjob", addJob, methods=['GET', 'POST'])
    return app

if __name__ == '__main__': 
    runApp()        
    app.run(host='0.0.0.0', debug=True) #, ssl_context='adhoc'