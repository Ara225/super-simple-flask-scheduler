from flask import Flask
from flask_testing import TestCase
import unittest
from app import *
from time import sleep
from datetime import datetime
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

if __name__ == '__main__':
    unittest.main()