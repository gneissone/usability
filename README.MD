#Usability Test
A Flask web app used for a short usability test.  
- - - -

##Getting started
Assuming you already have Python installed, here's what you need to get this puppy running.  
Note, it might be a good idea to set up a [virtual environment](http://flask.pocoo.org/docs/0.10/installation/#installation "Flask installation") to install your modules into.

###Install dependencies

	$ pip install Flask
	$ pip install WTForms
	$ pip install gspread

###Create a Google Sheet Workbook
1. It should be named "Usability Testing" (without the quotes).  
2. Create a second sheet in the same workbook, it should be called "Sheet2"  
3. Delete all the rows except the first one on both sheets. The app appends a row each time it runs and it will quite happily make that row 10,001 if your Google Form already has 10,000 rows.

###Obtain OAuth2 credentials from Google Developers Console  
See <http://gspread.readthedocs.org/en/latest/oauth2.html>  
Put the json file with your credentials into the static folder and rename it google.json.

###Give it a whirl

    $ cd {app directory}
	$ python routes.py

The console should now tell you the app is running. It's usually at http://127.0.0.1:5000/.

---
Known issues and caveats:

*	The app will fail if it can't connect to the Google Form. It will not fail gracefully.
*	The form for the test administrator is not password protected
