## How to install and run locally

Recommended to use Python 3

(Optional but recommended) Use a virtualenv:

`mkvirtualenv mineserve`


Install the requirements

`pip install -R requirements.txt`


Create a local MYSQL database and create an empty database called mineserve. You can set the database name, username and password in mineserve/default_settings.py


Run the server locally (eg. on port 8000):

`python application.py runserver 0.0.0.0:8000`
