'''
Contains test cases specifically related to job scheduling Should test every flashed error message
except the ones displayed on an exception as I haven't figured out how to trigger one yet
'''
from sys import path
path.append('../')
from flask import Flask
from flask_testing import TestCase
import unittest
from app import *
from time import sleep
from datetime import datetime
from flask_apscheduler.api import get_jobs

class TestScheduleJobs(TestCase):

    def create_app(self):
        return runApp()
    
    ### Test basic function - running jobs now

    def test_schedule_basic_job(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'typeSelector': jobType},
            follow_redirects=True
        )
        sleep(2)
        jobResults = self.client.get("/getjobsresults")
        self.assertIn(b'Hello World', jobResults.data)

    def test_schedule_with_no_completed_fields(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty or invalid job type selected', response.data)

    def test_schedule_with_only_jobId_completed(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty or invalid job type selected', response.data)
    
    def test_schedule_with_only_command_completed(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'command': 'echo Hello World'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty or invalid job type selected', response.data)

    def test_schedule_with_only_typeSelector_completed(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'typeSelector': jobType},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty or invalid job type selected', response.data)

    def test_schedule_with_invalid_typeSelector_input(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'typeSelector': 'NotAValidDate'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty or invalid job type selected', response.data)

    ### Tests for scheduling one off jobs

    def test_schedule_job_for_past_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType,  'DateTimeField': '2020-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Past date selected, please try again', response.data)

    def test_schedule_job_for_future_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'DateTimeField': str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(bytes('Job scheduled for ' + str(datetime.now().year + 1) + '-03-30 23:44', 'utf-8'), response.data)

    def test_schedule_job_with_invalid_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType,  'DateTimeField': 'NotAValidDAte'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid date provided, please try again', response.data)

    ### Tests for repeating jobs

    def test_schedule_job_seconds_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Seconds': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_minutes_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Minutes': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_hours_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Hours': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_days_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Days': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)
    
    def test_schedule_job_weeks_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Weeks': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_with_multiple_intervals(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Weeks': 5, 'Days': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_with_bad_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Seconds': 67},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid input - second, hour or minute interval field contains a value equal to or over sixty', response.data)

    def test_schedule_job_with_letters_in_interval_fields(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Days': 'NotANumber'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid input - non-number chars in interval field', response.data)

    ### Tests scheduling repeating jobs with start/end times

    def test_schedule_repeating_job_with_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Days': 1, 'StartDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        jobs = json.loads(get_jobs().get_data().decode('utf-8'))
        startDate = jobs[len(jobs)-1]['start_date'].split('.')[0].split(':')
        self.assertIn(b'Job scheduled to run at interval', response.data)
        self.assertEqual(startDate[0] + ':' + startDate[1], str(datetime.now().year + 1) + '-03-30T23:44')

    def test_schedule_repeating_job_with_end_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Seconds': 2, 'EndDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        jobs = json.loads(get_jobs().get_data().decode('utf-8'))
        endDate = jobs[len(jobs)-2]['end_date'].split('.')[0].split(':')
        self.assertIn(b'Job scheduled to run at interval', response.data)
        self.assertEqual(endDate[0] + ':' + endDate[1], str(datetime.now().year + 1) + '-03-30T23:44')

    def test_schedule_repeating_job_with_end_and_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Seconds': 2, 
            'StartDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44', 'EndDateTimeField':  str(datetime.now().year + 2) + '-03-30T23:44'},
            follow_redirects=True
        )
        jobs = json.loads(get_jobs().get_data().decode('utf-8'))
        startDate = jobs[len(jobs)-1]['start_date'].split('.')[0].split(':')
        endDate = jobs[len(jobs)-1]['end_date'].split('.')[0].split(':')
        self.assertIn(b'Job scheduled to run at interval', response.data)
        self.assertEqual(startDate[0] + ':' + startDate[1], str(datetime.now().year + 1) + '-03-30T23:44')
        self.assertEqual(endDate[0] + ':' + endDate[1], str(datetime.now().year + 2) + '-03-30T23:44')

    def test_schedule_repeating_job_with_past_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Days': 1, 'StartDateTimeField':  str(datetime.now().year + -1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Unable to schedule task, start date selected is in the past', response.data)

    def test_schedule_repeating_job_with_past_end_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': jobType, 'Seconds': 2, 'EndDateTimeField':  str(datetime.now().year + -1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Unable to schedule task, end date selected is in the past', response.data)

if __name__ == '__main__':
    jobType = 'Python Job'
    exec(unittest.main())