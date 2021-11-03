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
	
## API manual

Generate account

	url = http://localhost:8000/api/v1/accounts/singup
	method = POST
	body = {"email" : "",
		"phone":"",
		"nickname":"",
		"name":"",
		"password":""}

Login (email or phone)

	url = http://localhost:8000/api/v1/accounts/login
	method = POST
	body = {"email_or_phone" : "",
		"password":""}

Info (by request session user)

	url = http://localhost:8000/api/v1/accounts/info
	method = GET

Send SMS verification code to phone (for signup or changing password)

	url = http://localhost:8000/api/v1/accounts/generate
	method = POST
	body = {"phone":""}

Verify SMS code (by request session user)

	url = http://localhost:8000/api/v1/accounts/verify
	method = POST
	body = {"phone":"",
		"code":""}

Change password (without login with SMS verification code)

	url = http://localhost:8000/api/v1/accounts/verify
	method = POST
	body = {"phone":"",
		"code":"",
		"password":""}
