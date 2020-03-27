'''
## jobs.py: Functions and classes related to jobs
## Purpose
* Provide JobResults class for easy access to results of jobs 
* Provide functions for diffrent job types
'''

import subprocess
from datetime import datetime

class JobResults():
    '''
    JobResults object
    Properties:
    * stderr
    * stdout 
    * timeStarted
    * timeCompleted 
    * jobId 
    * returnCode 
    '''

    def __init__(self, stderr=None, stdout=None, timeStarted=None, timeCompleted=None, jobId=None, returnCode=None, jobType=None):
        self.stderr = stderr
        self.stdout = stdout
        self.timeStarted = timeStarted
        self.timeCompleted = timeCompleted
        self.jobId = jobId
        self.returnCode = returnCode
        self.jobType = jobType

def runShellCommandJob(command, jobId, JobResultsList):
    """
    Use subprocess to run a shell command, get the results, instigate a JobResults object with the result, and append it to JobResultsList 
        :param command: The command to run
        :param jobId: The name of the job
        :param JobResultsList: The list of completed jobs, which will be appended to
    """
    # instigate a JobResults object
    currentJobResults = JobResults()
    currentJobResults.jobId = jobId
    currentJobResults.timeStarted = datetime.now()
    try:
        # Run the command and collect the output as plain text, tidy up the line endings since they are fiddly
        currentJobResults.stdout = subprocess.check_output(command).decode('utf-8').replace('\r\n', '\n').replace('\\n', '\n')
        # Subprocess only allows this to succeed if the return code is 0
        currentJobResults.returnCode = 0
    # Process subprocess.CalledProcessError
    except subprocess.CalledProcessError as e:
        currentJobResults.stdout = e.stdout().replace('\r\n', '\n').replace('\\n', '\n')
        currentJobResults.stderr = e.stderr().replace('\r\n', '\n').replace('\\n', '\n')
        currentJobResults.returnCode = e.returncode
    # Other exceptions, we don't get return codes here so set to N/A
    except Exception as e:
        currentJobResults.stderr = str(e).replace('\r\n', '\n').replace('\\n', '\n')
        currentJobResults.returnCode = 'N/A'

    currentJobResults.timeCompleted = datetime.now()
    currentJobResults.jobType = 'Shell Job'
    JobResultsList.append(currentJobResults)