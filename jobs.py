'''
## jobs.py: Functions and classes related to jobs
## Purpose
* Provide functions for diffrent job types
'''
from yaml import dump
import subprocess
from datetime import datetime
from flask import flash
from re import match
from paramiko import RSAKey
from paramiko.auth_handler import AuthenticationException

def runShellCommandJob(command, jobId, JobResultsList, client):
    """
    Use subprocess to run a shell command, get the results, create a dict with the result, and append it to JobResultsList 
        :param command: The command to run
        :param jobId: The name of the job
        :parm JobResultsList: Jobs results list
        :parm client: Not used, for remote commands, exists only so they have the same number of args
    """
    # instigate a JobResults object
    currentJobResults = {}
    currentJobResults['jobId'] = jobId
    currentJobResults['timeStarted'] = datetime.now()
    try:
        # Run the command and collect the output as plain text, tidy up the line endings since they are fiddly
        currentJobResults['stdout'] = subprocess.check_output(command).decode('utf-8').replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        # Subprocess only allows this to succeed if the return code is 0
        currentJobResults['returnCode'] = 0
    # Process subprocess.CalledProcessError
    except subprocess.CalledProcessError as e:
        currentJobResults['stdout'] = e.stdout().replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        currentJobResults['stderr'] = e.stderr().replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        currentJobResults['returnCode'] = e.returncode
    # Other exceptions, we don't get return codes here
    except Exception as e:
        currentJobResults['stderr'] = str(e).replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        currentJobResults['returnCode'] = 'Unspecified'

    currentJobResults['timeCompleted'] = datetime.now()
    currentJobResults['jobType'] = 'Shell Job'
    currentJobResults['command'] = command
    JobResultsList.append(currentJobResults)

def runRemoteCommandJob(command, jobId, JobResultsList, client):
    """
    Use subprocess to run a shell command, get the results, create a dict with the result, and append it to JobResultsList 
        :param command: The command to run
        :param jobId: The name of the job
        :parm JobResultsList: Jobs results list
        :parm client: instance of SSHClient.Client
    """
    # instigate a JobResults object
    currentJobResults = {}
    currentJobResults['jobId'] = jobId
    currentJobResults['timeStarted'] = datetime.now()
    try:
        client.connect()
        currentJobResults['stdout'] = []
        currentJobResults['stderr'] = []
        tempVar = client.execute(command)
        # Run the command and collect the output as plain text, tidy up the line endings since they are fiddly
        for line in tempVar[0]:
            currentJobResults['stdout'].append(line.replace('\r\n', '').replace('\\n', '').replace('\n', '').replace("'", "\'"))
        for line in tempVar[1]:
            currentJobResults['stderr'].append(line.replace('\r\n', '').replace('\\n', '').replace('\n', '').replace("'", "\'"))
        currentJobResults['returnCode'] = 'Unspecified'
        # Process subprocess.CalledProcessError
    except AuthenticationException as e:
        currentJobResults['stderr'] = str(e).replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        currentJobResults['returnCode'] = 'Unspecified'
        return False
    except Exception as e:
        currentJobResults['stderr'] = str(e).replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        currentJobResults['returnCode'] = 'Unspecified'
    currentJobResults['timeCompleted'] = datetime.now()
    currentJobResults['jobType'] = 'Remote Job'
    currentJobResults['command'] = command
    JobResultsList.append(currentJobResults)

def scheduleOneOffJob(jobType, request, scheduler, JobResultsList, client=None):
    """
    Summary:
    Schedule one off job for a specified point in the future as specified in the DateTimeField of the form
    Parameters:
        :param jobType: The job type as contained in the function name - e.g. Shell, Python, Remote
        :param request: The POST request from the browser 
        :param scheduler: The Scheduler instance
        :param JobResultsList: The list of job results for the function to append to

    :returns: Boolean indicating whether the job was successfully scheduled
    """
    try:
        # Get a date time object out of the input
        whenToRun = datetime.fromisoformat(request.form['DateTimeField'])
        if compareDate(whenToRun):
            # Schedule a shell job, args are passed to the function not shell command
            scheduler.add_job(request.form['jobId'], '__main__:run' + jobType + 'CommandJob', 
                             args=(request.form['command'], request.form['jobId'], JobResultsList, client), 
                             trigger='date', run_date=whenToRun)
            flash('Job scheduled for ' + str(whenToRun))
            return True
        else:
            flash('Error: Past date selected, please try again')
            return False
    except Exception as e:
        if 'Invalid isoformat string' in str(e):
            flash('Error: Invalid date provided, please try again')
            return False            
        else:
            flash('Error: Unable to schedule task due to unexpected error ' + str(e))
            return False


def scheduleRepeatingJob(jobType, request, scheduler, JobResultsList, client=None):
    """
    Summary:
    Schedule repeating job at the intervals defined in the interval field 
    Parameters:
        :param jobType: The job type as contained in the function name - e.g. Shell, Python, Remote
        :param request: The POST request from the browser 
        :param scheduler: The Scheduler instance
        :param JobResultsList: The list of job results for the function to append to
    :returns: Boolean indicating whether the job was successfully scheduled
    """
    try:
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
                    return False
            else:
                intervalFields[count] = 0
            count += 1
        if intervalFieldsHaveValue == True:
            # This ensures that the start and end date fields are valid and are not in the past
            schedulerEnd = request.form.get('EndDateTimeField', None)
            schedulerStart = request.form.get('StartDateTimeField', None)
            if schedulerStart == '':
                schedulerStart = None
            elif schedulerStart != None: 
                if not compareDate(datetime.fromisoformat(schedulerStart)):
                    flash('Error: Unable to schedule task, start date selected is in the past')
                    return False
            if schedulerEnd == '':
                schedulerEnd = None
            elif schedulerEnd != None:
                if not compareDate(datetime.fromisoformat(schedulerEnd)):
                    flash('Error: Unable to schedule task, end date selected is in the past')
                    return False 
            # Schedule a job to run at the requested interval, args are passed to the function not command
            scheduler.add_job(request.form['jobId'], '__main__:run' + jobType + 'CommandJob', 
                             args=(request.form['command'], request.form['jobId'], JobResultsList, client), 
                             trigger='interval', seconds=intervalFields[0], minutes=intervalFields[1], 
                             hours=intervalFields[2], days=intervalFields[3], weeks=intervalFields[4], 
                             start_date=schedulerStart, end_date=schedulerEnd)
            # This causes this to be displayed on the screen under the form
            flash('Job scheduled to run at interval')
            return True
        else:
            return False 
    except Exception as e:
        if 'Invalid isoformat string' in str(e):
            flash('Error: Invalid date provided, please try again')
            return False            
        else:
            flash('Error: Unable to schedule task due to unexpected error ' + str(e))
            return False

def scheduleCronJob(jobType, request, scheduler, JobResultsList, client=None):
    """
    Summary:
    Schedule cron jobs with the cron expression defined in the cron field 
    Parameters:
        :param jobType: The job type as contained in the function name - e.g. Shell, Python, Remote
        :param request: The POST request from the browser 
        :param scheduler: The Scheduler instance
        :param JobResultsList: The list of job results for the function to append to
    :returns: Boolean indicating whether the job was successfully scheduled
    """
    try:
        cronFieldsHaveValue = None
        # These can be returned even if they have nothing or only whitespace in them so we need to do some processing
        cronFields = [
            request.form.get('CronSeconds', ''), 
            request.form.get('CronMinutes', ''), 
            request.form.get('CronHours', ''), 
            request.form.get('CronDayOfWeek', ''), 
            request.form.get('CronWeeks', ''), 
            request.form.get('CronDays', ''), 
            request.form.get('CronMonth', ''), 
            request.form.get('CronYear', '')
        ]
        # These fields come out as strings so need to do some processing to make them work
        count = 0
        for i in cronFields:
            # If field isn't blank
            if i != '' and i.replace(' ', '') != '' and i != None:
                cronFieldsHaveValue = True
                cronFields[count] = int(i)
            # Defaults to * meaning any value 
            else:
                cronFields[count] = '*'
            count += 1
        if cronFieldsHaveValue == True:
            # Schedule a job to run at the requested interval, args are passed to the function not command
            scheduler.add_job(request.form['jobId'], '__main__:run' + jobType + 'CommandJob', 
                             args=(request.form['command'], request.form['jobId'], JobResultsList, client), 
                             trigger='cron', 
                             year=cronFields[7],
                             month=cronFields[6],
                             day=cronFields[5],
                             week=cronFields[4],
                             day_of_week=cronFields[3],
                             hour=cronFields[2],
                             minute=cronFields[1],
                             second=cronFields[0]
                            )

            # This causes this to be displayed on the screen under the form
            flash('Job scheduled to run at cron interval')
            return True
        else:
            flash('Error: Unable to schedule cron type job - cron fields have no value')
            return False
    except Exception as e:
        flash('Error: Unable to schedule task due to unexpected error ' + str(e))
        return False

def runJobNow(jobType, request, scheduler, JobResultsList, client=None):
    """
    Summary:
    Run a job right now
    Parameters:
        :param jobType: The job type as contained in the function name - e.g. Shell, Python, Remote
        :param request: The POST request from the browser 
        :param scheduler: The Scheduler instance
        :param JobResultsList: The list of job results for the function to append to
    :returns: Boolean indicating whether the job was successfully scheduled
    """
    try:
        # Schedule a job now, args are passed to the function not command
        scheduler.add_job(request.form['jobId'], '__main__:run' + jobType + 'CommandJob', 
                         args=(request.form['command'], request.form['jobId'], JobResultsList, client), 
                         trigger='date', run_date=datetime.now())
        # This causes this to be displayed on the screen under the form
        flash('Job scheduled to run now')
        return True
    except Exception as e:
        flash('Error: Unable to schedule task due to unexpected error ' + str(e))
        return False

def compareDate(dateToCompare):
    difference = dateToCompare - datetime.now()
    # This checks if the date given is in the past. The days will be at least -1 if  the day is equal or the same
    # The problem is when it's the same day - the date always results in -1 so we deal with the special case first
    if dateToCompare.day == datetime.now().day and dateToCompare.month == datetime.now().month and dateToCompare.year == datetime.now().year:
        if dateToCompare.minute >= datetime.now().minute and dateToCompare.hour > datetime.now().hour:
            return True
        elif dateToCompare.minute > datetime.now().minute and dateToCompare.hour == datetime.now().hour:
            return True
        else:
            return False
    elif difference.days > 0:
        return True
    else:
        return False