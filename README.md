## How to install and run locally

Recommended to use Python 3

(Optional but recommended) Use a virtualenv:

`mkvirtualenv mineserve`


Install the requirements

`pip install -R requirements.txt`


Create a local MYSQL database and create an empty database called mineserve. You can set the database name, username and password in mineserve/default_settings.py. Database will be populated automatically when app launches.


Run the server locally (eg. on port 8000):

`python application.py runserver 0.0.0.0:8000`


debug is set to true by default so launching server will create mock servers.

To get to admin console, log in as the admin user (adventureservers@kolabnow.com by default) and password which is set in mineserve/default_settings.py, then go to /admin
