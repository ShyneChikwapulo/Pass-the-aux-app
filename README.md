# Pass-the-Aux-App

## Setup Instructions
### Note using python 3.10

First cd into your desired   folder  .
```bash
cd "Pass-the-Aux"
```

 ### Create the virtual environment
 ```bash
 # For Windows
python -m venv venv
```
### Activate the virtual environment
```bash
venv\Scripts\activate
```
### Install Required Python Modules
```bash
pip install -r requirements.txt
```
### Start Web Server

To start the web server you need to run the following sequence of commands.


Next run the django web server.
```bash
python manage.py runserver
```
### Install Node.js

### Install Node Modules

First cd into the frontend folder.
```bash
cd frontend
```
Next install all dependicies.
```bash
npm i
```
Compile the Front-End

Run the production compile script
```bash
npm run build
```
or for development:
```bash
npm run dev
```
