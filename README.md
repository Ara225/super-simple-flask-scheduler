# Super Simple Flask Schedular 

## What?
Basically, it's supposed to be a simple and easy to use/understand useful Python GUI web based schedular.

## Why? 
Mainly a personal keep-busy sort of project. Loosely designed to fill a gap in that there aren't any 
complete simple web schedulers (that I could find). It's not really production quality code though so. 

## Files
app.py - App entry point python3 ./app.py to run with development web server 
forms.py - forms classes and functions
jobs.py - Jobs classes and functions
templates - Jinja2 templates for display
static - CSS files and some extra JS functions

## Tests Files
test_schedule_shell_jobs.py - Test scheduling shell jobs
test_general_app.py - Other tests

## TODO
* Implement optional persistent job storage 
* Implement Python job functionality
* Implement basic remote job functionality
* Implement authentication 
* Eliminate use of global vars
* Improve the cleanup job