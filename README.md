# Django-DRF-UserAPI

Python Django RestFramework - User API (Signup, Login, My Info, Change Password)
with JWT token


## Features

* Django embedded password validation
* JWT token for further APIs
* Custom user model

### Handling Configuration (config.ini)

* JWT Expire time
* OTP Generation term, count
* Login try count

## Installation	

### Requirements

* Python 3.5 or higher


### Install
Clone git repository

	$ git clone http://github.com/HJSAMO/Django-DRF-UserAPI.git
  
Generate virtual environment (Optional)

	$ virtualenv venv
	$ source venv/bin/activate
  
Install all required libraries

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

	url = http://localhost:8000/api/v1/accounts/signup
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

	url = http://localhost:8000/api/v1/accounts/generation
	method = POST
	body = {"phone":""}

Verify SMS code (by request session user)

	url = http://localhost:8000/api/v1/accounts/verification
	method = POST
	body = {"phone":"",
		"otp":""}

Change password (without login with SMS verification code)

	url = http://localhost:8000/api/v1/accounts/info
	method = POST
	body = {"phone":"",
		"otp":"",
		"password":""}

