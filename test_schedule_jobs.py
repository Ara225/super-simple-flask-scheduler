'''
Contains test cases specifically related to job scheduling Should test every flashed error message
except the ones displayed on an exception as I haven't figured out how to trigger one yet
'''
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
            data={'jobId': 'TestJob', 'command': 'echo Hello World'},
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
        self.assertIn(b'Error: Required form fields empty', response.data)

    def test_schedule_with_only_jobId_completed(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty', response.data)
    
    def test_schedule_with_only_command_completed(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'command': 'echo Hello World'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Required form fields empty', response.data)

    ### Tests for scheduling one off jobs

    def test_schedule_job_for_past_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"',  'DateTimeField': '2020-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Past date selected, please try again', response.data)

    def test_schedule_job_for_future_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'DateTimeField': str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(bytes('Job scheduled for ' + str(datetime.now().year + 1) + '-03-30 23:44', 'utf-8'), response.data)

    def test_schedule_job_with_invalid_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"',  'DateTimeField': 'NotAValidDAte'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid date provided, please try again', response.data)

    ### Tests for repeating jobs

    def test_schedule_job_seconds_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Seconds': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_minutes_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Minutes': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_hours_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Hours': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_days_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Days': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)
    
    def test_schedule_job_weeks_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Weeks': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_with_multiple_intervals(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Weeks': 5, 'Days': 5},
            follow_redirects=True
        )
        self.assertIn(b'Job scheduled to run at interval', response.data)

    def test_schedule_job_with_letters_in_interval_fields(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'Days': 'NotANumber'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid input - non-number chars in interval field', response.data)

    ### Tests scheduling repeating jobs with start/end times

    def test_schedule_repeating_job_with_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'Days': 1, 'StartDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44'},
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
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'Seconds': 2, 'EndDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44'},
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
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'Seconds': 2, 
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
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'Days': 1, 'StartDateTimeField':  str(datetime.now().year + -1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Unable to schedule task, start date selected is in the past', response.data)

    def test_schedule_repeating_job_with_past_end_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'Seconds': 2, 'EndDateTimeField':  str(datetime.now().year + -1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Unable to schedule task, end date selected is in the past', response.data)

    def test_schedule_job_with_host_and_no_user(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'targetHost': 'NotAValidHost'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Target host user not provided', response.data)

    def test_schedule_job_with_host_and_user_no_password(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'targetHost': 'NotAValidHost', 'targetHostUser': 'NotAValidUser'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Neither password or SSH key provided', response.data)

    def test_schedule_job_with_host_user_and_invalid_password(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'targetHost': 'NotAValidHost', 'targetHostUser': 'NotAValidUser', 'targetHostPassword': 'NotAValidPassword'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Test connection failed, job not scheduled due to unexpected error', response.data)

    def test_schedule_job_with_user_and_no_host(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'targetHostUser': 'NotAValidUser'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Target host not supplied', response.data)

    def test_schedule_job_with_password_and_no_host(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'targetHostPassword': 'NotAValidPassword'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Target host not supplied', response.data)

    def test_schedule_job_with_checkbox_and_no_host(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'shouldUseExistingSSHKey': 'on'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Target host not supplied', response.data)


    def test_schedule_job_with_ssh_key_and_no_host(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'targetHostSSHKey': 'NotAValidSSHKey'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Target host not supplied', response.data)

    def test_schedule_job_with_cron_timings(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={
                'jobId': 'TestJob', 
                'command': 'echo Hello World', 
                'ShouldUseCron': 'on', 
                'CronSeconds': 1,
                'CronMinutes': 2,
                'CronHours': 3,
                'CronDayOfWeek': 4,
                'CronWeeks': 5,
                'CronDays': 6,
                'CronMonth': 7,
                'CronYear': 2021
            },
            follow_redirects=True
        )
        job = self.client.get("/getjobs")
        self.assertIn(b'Job scheduled to run at cron interval', response.data)
        self.assertIn(b'1 Second of Minute', job.data)
        self.assertIn(b'2 Minute of Hour', job.data)
        self.assertIn(b'3 Hour of Day', job.data)
        self.assertIn(b'4 Day of the Week', job.data)
        self.assertIn(b'5 Week of Month', job.data)
        self.assertIn(b'6 Days of the month', job.data)
        self.assertIn(b'7 Month of the year', job.data)
        self.assertIn(b'2021 Year', job.data)


    def test_schedule_job_with_no_cron_fields_completed(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'ShouldUseCron': 'on'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Unable to schedule cron type job - cron fields have no value', response.data)

if __name__ == '__main__':
    unittest.main()