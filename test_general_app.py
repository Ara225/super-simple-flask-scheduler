'''
Tests that don't deal with job scheduling 
'''
from flask import Flask
from flask_testing import TestCase
import unittest
from app import *
from flask_apscheduler.api import get_jobs

class TestGeneralApp(TestCase):

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
    
    def test_delete_job_from_getjobs(self):
        self.client.get("/getjobs")
        response = self.client.post(
            '/getjobs',
            data={'RemoveJob': 'CleanupJob'},
            follow_redirects=True
        )
        self.assertIn(b'Job successfully deleted', response.data)

    def test_delete_job_with_bad_name(self):
        self.client.get("/")
        response = self.client.post(
            '/',
            data={'RemoveJob': 'NotAValidJob'},
            follow_redirects=True
        )
        self.assertIn(b'Error: Unknown issue occurred: &#39;No job by the id of NotAValidJob was found&#39;', response.data)

    def test_delete_job_with_no_name(self):
        self.client.get("/")
        response = self.client.post(
            '/',
            data={'RemoveJob': ''},
            follow_redirects=True
        )
        self.assertIn(b'Error: Hidden form field tampered with', response.data)

if __name__ == '__main__':
    unittest.main()