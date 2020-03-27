# Super Simple Flask Schedular 

## What?
Basically, it's supposed to be the simplest and easiest to use/understand useful Python GUI web based schedular.

## Why? 
Mainly a personal keep-busy sort of project. Loosely designed to fill a gap in that there aren't any complete simple web 
schedulers (that I could find).

## Is it useful? 
Not right now. It may be in the future.

## TODO
* Implement optional persistent job storage 
* Implement Python job functionality
* Improve GUI of jobs and jobs result screen 
* Implement basic remote job functionality
* Implement actual scheduling function rather than just running everything now
* Implement authentication 
* Write some tests
* Eliminate use of global vars

## Contributions/Thoughts
Very welcome

## Release Notes
### 0.0.1
Outline of app, capability to run shell commands now, and store results in memory.

### 0.0.2
Refactoring, documentation of the code 

# Overview Of Files
## app.py: App main entry point 

### Imports:
#### Standard Library
* datetime
* random
* string
* sleep from time
* json
##### Internal
* jobs - Definition of the diffrent job types and the JobResults class to contain results
* forms - Definition of various forms used
##### Other
* flask - Basic web front end functionality
* flask_apscheduler - scheduler functionality intergrated with Flask
* flask_apscheduler.api get_jobs - Return jobs objects in Json

### Purpose
* Initialize the scheduler and Flask app
* Add routes to the app

### Routes
* / -> index() | Supports: GET
* /getjobs -> getJobs() | Supports: GET
* /getjobsresults -> getJobsResults() | Supports: GET
* /addjob -> addJob() | Supports: GET POST

## jobs.py: Functions and classes related to jobs
## Purpose
* Provide JobResults class for easy access to results of jobs 
* Provide functions for different job types

## Forms.py: Functions and classes related to jobs
