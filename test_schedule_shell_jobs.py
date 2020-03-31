from flask import Flask
from flask_testing import TestCase
import unittest
from app import *
from time import sleep
from datetime import datetime
from flask_apscheduler.api import get_jobs

class TestScheduleShellJob(TestCase):

    def create_app(self):
        return runApp()

    def test_schedule_basic_shell_job(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo Hello World', 'typeSelector': 'Shell Job'},
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
        self.assertIn(b'Error: Required Form Fields Empty', response.data)

    def test_schedule_job_for_past_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job',  'DateTimeField': '2020-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Past date selected, please try again', response.data)

    def test_schedule_job_for_future_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'DateTimeField': str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(bytes('Shell job scheduled for ' + str(datetime.now().year + 1) + '-03-30 23:44', 'utf-8'), response.data)

    def test_schedule_job_seconds_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Seconds': 5},
            follow_redirects=True
        )
        self.assertIn(b'Shell job scheduled to run at interval', response.data)

    def test_schedule_job_minutes_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Minutes': 5},
            follow_redirects=True
        )
        self.assertIn(b'Shell job scheduled to run at interval', response.data)

    def test_schedule_job_hours_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Hours': 5},
            follow_redirects=True
        )
        self.assertIn(b'Shell job scheduled to run at interval', response.data)

    def test_schedule_job_days_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Days': 5},
            follow_redirects=True
        )
        self.assertIn(b'Shell job scheduled to run at interval', response.data)
    
    def test_schedule_job_weeks_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Weeks': 5},
            follow_redirects=True
        )
        self.assertIn(b'Shell job scheduled to run at interval', response.data)

    def test_schedule_job_with_multiple_intervals(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Weeks': 5, 'Days': 5},
            follow_redirects=True
        )
        self.assertIn(b'Shell job scheduled to run at interval', response.data)

    def test_schedule_job_with_bad_interval(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Seconds': 67},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid input - second, hour or minute interval field contains a value equal to or over sixty', response.data)

    def test_schedule_job_with_letters_in_interval_fields(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Days': 'NotANumber'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Invalid input - non-number chars in interval field', response.data)


    def test_schedule_repeating_job_with_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Days': 1, 'StartDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        jobs = json.loads(get_jobs().get_data().decode('utf-8'))
        startDate = jobs[len(jobs)-1]['start_date'].split('.')[0].split(':')
        self.assertIn(b'Shell job scheduled to run at interval', response.data)
        self.assertEqual(startDate[0] + ':' + startDate[1], str(datetime.now().year + 1) + '-03-30T23:44')

    def test_schedule_repeating_job_with_end_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Seconds': 2, 'EndDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        jobs = json.loads(get_jobs().get_data().decode('utf-8'))
        endDate = jobs[len(jobs)-2]['end_date'].split('.')[0].split(':')
        self.assertIn(b'Shell job scheduled to run at interval', response.data)
        self.assertEqual(endDate[0] + ':' + endDate[1], str(datetime.now().year + 1) + '-03-30T23:44')

    def test_schedule_repeating_job_with_end_and_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Seconds': 2, 
            'StartDateTimeField':  str(datetime.now().year + 1) + '-03-30T23:44', 'EndDateTimeField':  str(datetime.now().year + 2) + '-03-30T23:44'},
            follow_redirects=True
        )
        jobs = json.loads(get_jobs().get_data().decode('utf-8'))
        startDate = jobs[len(jobs)-1]['start_date'].split('.')[0].split(':')
        endDate = jobs[len(jobs)-1]['end_date'].split('.')[0].split(':')
        self.assertIn(b'Shell job scheduled to run at interval', response.data)
        self.assertEqual(startDate[0] + ':' + startDate[1], str(datetime.now().year + 1) + '-03-30T23:44')
        self.assertEqual(endDate[0] + ':' + endDate[1], str(datetime.now().year + 2) + '-03-30T23:44')

    def test_schedule_repeating_job_with_past_start_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Days': 1, 'StartDateTimeField':  str(datetime.now().year + -1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Past start date selected, please try again', response.data)

    def test_schedule_repeating_job_with_past_end_time(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'StartTimeTestJob', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'Seconds': 2, 'EndDateTimeField':  str(datetime.now().year + -1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Past end date selected, please try again', response.data)

if __name__ == '__main__':
    unittest.main()