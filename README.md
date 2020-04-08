# Super Simple Flask Schedular 

## What?
Basically, it's supposed to be a simple and easy to use/understand useful Python GUI web based scheduler.
It supports running remote shell commands, local shell commands, persistent job storage and various 
scheduling choices, however, it's just a personal messing around project so the code quality probably 
isn't up to scratch

## Files
app.py - App entry point. python3 ./app.py to run with development web server

forms.py - forms classes and functions

jobs.py - Jobs classes and functions

SSHclient.py - Contains the Client class which does the SSH connection work

## Folders
templates - Jinja2 templates for display

static - CSS files and some extra JS functions

## Tests Files
.\test_schedule_shell_jobs.py - Test scheduling jobs

.\test_general_app.py - Other tests

## TODO
* Implement authentication 
