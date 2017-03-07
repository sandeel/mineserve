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


## Running on AWS

The manage.sh script in the root directory should be able to automatically spin up the needed infrastructure on AWS. You'll need to have the AWS CLI tool [1] installed and have authentication set up, as the script will make use of AWS CLI calls.

### Usage:

To spin up the resources:

    ./manage.sh spin-up

Note you'll need to authenticate the script to Github with Oauth token in environment variables MSV_GITHUB_TOKEN. This can be done as a one-liner like

    GITHUB_TOKEN=12345 ./manage.sh spin-up

To terminate all the resources:

    ./manage.sh spin-down

[1] AWS CLI https://aws.amazon.com/cli/tool 
