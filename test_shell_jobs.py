from flask import Flask
from flask_testing import TestCase
import unittest
from app import *
from time import sleep
from datetime import datetime


class TestApp(TestCase):

    def create_app(self):
        return runApp()

    def test_root_url(self):
        self.assert200(self.client.get("/"))

    def test_get_jobs_url(self):
        self.assert200(self.client.get("/getjobs"))

    def test_get_jobs_results_url(self):
        self.assert200(self.client.get("/getjobsresults"))

    def test_add_jobs_url(self):
        self.assert200(self.client.get("/addjob"))

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
            data={'jobId': 'TestJob2', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job',  'DateTimeField': '2020-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Past date selected, please try again', response.data)

    def test_schedule_job_for_future_date(self):
        self.client.get("/addjob")
        response = self.client.post(
            '/addjob',
            data={'jobId': 'TestJob2', 'command': 'echo "Hello World"', 'typeSelector': 'Shell Job', 'DateTimeField': str(datetime.now().year + 1) + '-03-30T23:44'},
            follow_redirects=True
        )
        self.assertIn(bytes('Shell job scheduled for ' + str(datetime.now().year + 1) + '-03-30 23:44', 'utf-8'), response.data)

    def test_schedule_job_seconds_interval(self):
        pass

    def test_schedule_job_minutes_interval(self):
        pass

    def test_schedule_job_hours_interval(self):
        pass

    def test_schedule_job_days_interval(self):
        pass
    
    def test_schedule_job_weeks_interval(self):
        pass

    def test_schedule_job_with_bad_seconds_interval(self):
        pass

    def test_schedule_job_with_letters_in_interval_fields(self):
        pass

    def test_schedule_repeating_job_with_start_time(self):
        pass

    def test_schedule_repeating_job_with_end_time(self):
        pass

    def test_schedule_repeating_job_with_end_and_start_time(self):
        pass   

if __name__ == '__main__':
    unittest.main()