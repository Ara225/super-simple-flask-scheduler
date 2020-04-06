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
Finish interval scheduling, add a cleanup job to tidy JobResultsList, remove unused CSS

### 0.0.6
Start implementing tests

### 0.0.7
Finish tests, refactor jobs code

### 0.0.8
Tidy and enhance frontend code

### 0.0.9
Implement basic Python job functionality, no stdout capturing 

### 0.1.1
Substantial front end improvements, completely changed the add jobs page and added some stupid client side validation
Decided to limit to shell jobs (local or remote). Python jobs were a bit more completed to implement 

### 0.1.2
Bug fixes and minor improvements

### 0.1.3
Significant frontend changes

### 0.1.4
Implement deleting pending jobs

### 0.1.5
Remove the limitation on seconds, hours and minutes Not sure why I limited it to 60.

### 0.1.6
Move config into yaml file and implement custom jobstores and executors - see Config.yaml for examples

### 0.1.7
Add requirements.txt, move test files into main folder again (Config.yaml was causing problems), ensure
new function was covered by tests 

### 0.1.8
Implement cron job scheduling type 