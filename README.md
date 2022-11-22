# Instant Variable Search App

The project implements a flask application that can be deployed a service in the Google Application Engine, using Datastore as a database.
The app implemenets the REST API below and assuming that each fetch/save access methods in the Datastore is O(1), then every method below is O(1) except the /clean method

# Setup
* Create an isolation Python enviroment
* Install the project requirements: > pip install -r requirements.txt

# Usage (Locally)
* Add a main function to the main.py file to run the app with a desired port
* Run the application: > python3 main.py
* In your web browser, enter the following address: > http://localhost:[port]

# Usage (As a GAE app)
* Create a GCP account
* Create a new project
* Add project's id to the main.py file
* Follow the instructions [here](https://cloud.google.com/appengine/docs/standard/python3/building-app/deploying-web-service) to deploy the app
* In your web browser, access the app on the following link: > https://[PROJECT_ID].[REGION_ID].r.appspot.com

# REST API:

The application includes the implemenation of the following:

1) **(POST) /set?name={variable_name}&value={variable_value}**

Set the variable variable_name to the value variable_value, neither variable names nor values will contain spaces. 

2) **(GET) /get?name={variable_name}**

Returns the value of the variable variable_name or NOT FOUND if the variable is not set.

3) **(PUT) – /unset?name={variable_name}**

  Unset the variable variable_name, making it just like the variable was never set.

4) **(GET) /numequalto?value={variable_value}**

  Returns the number of variables that are currently set to variable_value. If no variables equal that value, returns 0.

5) **(POST) /undo**

  Undo the most recent SET/UNSET command. 
  If more than one consecutive UNDO command is issued, the original commands will be undone in the reverse order of their execution.
  Returns the name and value of the changed variable (after the undo) if successful, or NOT FOUND if no commands can be undone.

6) **(POST) /redo**

  Redo the most recent SET/UNSET command which was undone. 
  If more than one consecutive REDO command is issued, the original commands will be redone in the original order of their execution. 
  If another set/unset command was issued after an UNDO, the REDO command will do nothing. 
  Returns the name and value of the changed variable (after the redo) if successful, or returns NOT FOUND if no commands can be re-done. 

7) **(DELETE) /clean**

  Removes all the data from the application

# Running example
You can find a running example of the app [here](https://fast-simon-instantsearch.as.r.appspot.com) (Make sure to add the desired endpoint to the url)
