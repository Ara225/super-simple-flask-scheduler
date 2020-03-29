'''
## jobs.py: Functions and classes related to jobs
## Purpose
* Provide JobResults class for easy access to results of jobs 
* Provide functions for diffrent job types
'''
from yaml import dump
import subprocess
from datetime import datetime

def runShellCommandJob(command, jobId, JobResultsList):
    """
    Use subprocess to run a shell command, get the results, instigate a JobResults object with the result, and append it to JobResultsList 
        :param command: The command to run
        :param jobId: The name of the job
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
    # Other exceptions, we don't get return codes here so set to N/A
    except Exception as e:
        currentJobResults['stderr'] = str(e).replace('\r\n', '\n').replace('\\n', '\n').replace("'", "\'").split('\n')
        currentJobResults['returnCode'] = 'N/A'

    currentJobResults['timeCompleted'] = datetime.now()
    currentJobResults['jobType'] = 'Shell Job'
    JobResultsList.append(currentJobResults)