# Django-DRF-UserAPI

Python Django RestFramework - User API (Signup, Login, My Info, Change Password)
	
## Installation	
### Requirements
* Python 3.5 or higher

### Install
Clone git repository

	$ git clone http://github.com/HJSAMO/Django-DRF-UserAPI.git
  
Generate virtual environment (Optional)

	$ virtualenv venv
	$ cd venv
	$ source bin/activate
  
Install all required libraries

	$ cd user_api
	$ pip install -r requirements.txt
  
Create database tables

	$ python manage.py makemigrations
	$ python manage.py migrate
  
Create admin account

	$ python manage.py createsuperuser
  
### Start a server for development
	$ python manage.py runserver 0.0.0.0:8000
