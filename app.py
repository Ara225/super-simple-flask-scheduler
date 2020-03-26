from flask import Flask, redirect, url_for, render_template, request, flash
from flask_apscheduler import APScheduler
from flask_apscheduler.api import get_jobs
from datetime import datetime
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField
import random
import string
from time import sleep
import json
import subprocess

app = None
scheduler = None
JobResultsList = []


class Config(object):
    JOBS = []
    SCHEDULER_API_ENABLED = False

class JobResults():
    def __init__(self, stderr=None, stdout=None, timeStarted=None, timeCompleted=None, jobId=None, returnCode=None):
        self.stderr = stderr
        self.stdout = stdout
        self.timeStarted = timeStarted
        self.timeCompleted = timeCompleted
        self.jobId = jobId
        self.returnCode = returnCode

def runShellCommandJob(command, jobId):
    currentJobResults = JobResults()
    currentJobResults.jobId = jobId
    currentJobResults.timeStarted = datetime.now()
    try:
        currentJobResults.stdout = subprocess.check_output(command).decode('utf-8')
        currentJobResults.returnCode = 0
    except subprocess.CalledProcessError as e:
        currentJobResults.stderr = e.output
        currentJobResults.returnCode = e.returncode
    except Exception as e:
        currentJobResults.stderr = str(e)
        currentJobResults.returnCode = -1
    currentJobResults.timeCompleted = datetime.now()
    global JobResultsList
    JobResultsList.append(currentJobResults)
    
def index():    
    return render_template('MainPageTemplate.html')

class ReusableForm(Form):
    jobId = TextField('jobId', validators=[validators.DataRequired()])
    command = TextField('command', validators=[validators.DataRequired()])
    typeSelector = SelectField('typeSelector', validators=[validators.none_of([('', '')])], choices=[('', ''), ('Python Job', 'Python Job'), ('Shell Job', 'Shell Job')])

def addJob():
    letters = string.ascii_letters + string.digits
    app.config['SECRET_KEY'] =  ''.join(random.choice(letters) for i in range(60))
    form = ReusableForm(request.form)
    if request.method == 'POST':
        if form.validate() and request.form['typeSelector'] == 'Shell Job':
            scheduler.add_job(request.form['jobId'], '__main__:runShellCommandJob', 
                        args=(request.form['command'], request.form['jobId']),
                        trigger='date', run_date=datetime.now())
            flash('Job added')
        elif request.form['typeSelector'] == 'Python Job':
            flash('Error: Not yet implemented')
        elif not form.validate(): 
            flash('Error: All the form fields are required. ')
        else:
            flash('Error: Unknown issue occurred')
    return render_template('AddJobPageTemplate.html')

def getJobs():   
    jobs = json.loads(get_jobs().get_data().decode('utf-8'))
    return render_template('ViewJobsPageTemplate.html', jobs=jobs) 

def getJobsResults():   
    return render_template('JobsResultPageTemplate.html', jobs=JobResultsList) 

def run():
    global app 
    app = Flask(__name__)
    app.config.from_object(Config())
    global scheduler 
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.add_url_rule("/", "/", index, methods=['GET'])
    app.add_url_rule("/getjobs", "/getjobs", getJobs, methods=['GET'])
    app.add_url_rule("/getjobsresults", "/getjobsresults", getJobsResults, methods=['GET'])
    app.add_url_rule("/addjob", "/addjob", addJob, methods=['GET', 'POST'])

if __name__ == '__main__': 
    run()        
    app.run(host='0.0.0.0', debug=True)