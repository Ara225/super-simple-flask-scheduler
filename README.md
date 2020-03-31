# Super Simple Flask Schedular 

## What?
Basically, it's supposed to be a simple and easy to use/understand useful Python GUI web based schedular.

## Why? 
Mainly a personal keep-busy sort of project. Loosely designed to fill a gap in that there aren't any 
complete simple web schedulers (that I could find). It's not particularly good though so.

## Files
app.py - App entry point python3 ./app.py to run with development web server 
forms.py - forms classes and functions
jobs.py - Jobs classes and functions
templates - Jinja2 templates for display
static - CSS files 

## Test Files
test_schedule_shell_jobs.py - Test scheduling shell jobs

## TODO
* Implement optional persistent job storage 
* Implement Python job functionality
* Improve GUI of jobs and jobs result screen 
* Implement basic remote job functionality
* Implement authentication 
* Write some tests
* Eliminate use of global vars
* Improve the cleanup job

## Change log
### 0.0.1
Outline of app, capability to run shell commands now, and store results in memory.

### 0.0.2
Refactoring, documentation of the code 

### 0.0.3
Add basic scheduling function, play with the frontend a bit

### 0.0.4
Start implementing interval scheduling

### 0.0.5 
Finish interval scheduling, add a cleanup job to tidy JobResultsList, remove unused JS

### 0.0.6
Start implementing tests
