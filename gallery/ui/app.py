from flask import Flask
from flask import request
from flask import render_template

import psycopg2
import json
from secrets import get_secret_image_gallery

connection = None

def get_secret():
    jsonString = get_secret_image_gallery()
    return json.loads(jsonString)

def get_password(secret):
    return secret['password']

def get_host(secret):
    return secret['host']

def get_username(secret):
    return secret['username']

def get_dbname(secret):
    return secret['database_name']

def connect():
    global connection
    secret = get_secret()
    connection = psycopg2.connect(host=get_host(secret), dbname=get_dbname(secret), user=get_username(secret), password=get_password(secret))

def execute(query,args=None):
    global connection
    cursor = connection.cursor()
    if not args:
        cursor.execute(query)
    else:
        cursor.execute(query, args)    
    return cursor

def user_exists(username):
    if execute("SELECT * FROM users WHERE username=%s;",(username,)).rowcount == 0: 
        return False
    else: 
        return True

def list_users():
    print("list_users") 
    row_string = "{username:10}\t{password:10}\t{full_name:20}"
    print(row_string.format(username="username",password="password",full_name="full name"))
    print("---------------------------------------------")
    for row in execute('select * from users'):
        print(row_string.format(username=row[0],password=row[1],full_name=row[2]))
    print()
        
def add_user(username,password,full_name):
    if user_exists(username): 
        print("Error:  user already exists.")
    else:
        execute("INSERT INTO users (username, password, full_name) VALUES (%s,%s,%s);",(username,password,full_name))
    
def edit_user(username,password,full_name):
    if not user_exists(username): 
        print("No such user.")
    elif password != "" and full_name != "":
        execute("UPDATE users SET password=%s,full_name=%s WHERE username=%s;",(password,full_name,username))
    elif password != "" and full_name == "":
        execute("UPDATE users SET password=%s WHERE username=%s;",(password,username))
    elif password == "" and full_name != "":
        execute("UPDATE users SET full_name=%s WHERE username=%s;",(full_name,username))
        
def delete_user(username):
    if not user_exists(username): 
        print("No such user.")
    else:
        execute("DELETE FROM users WHERE username=%s;",(username,))
    


app = Flask(__name__)

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html>
    <head>
        <title>Christian Nightingale's Auburn Python Web App</title>
        <meta charset="utf-8" />
    </head>
    <body>
        <h1>Christian Nightingale's Auburn Python Web App</h1>
    </body>
</html>
"""

@app.route('/admin')
def admin():
    list_users()
    return 'Goodbye'

@app.route('/greet/<name>')
def greet(name):
    return 'Nice to meet you ' + name

@app.route('/add/<int:x>/<int:y>', methods = ['GET'])
def add(x, y):
    return 'The sum is ' + str(x + y)

@app.route('/mult')
def mult():
    x = request.args['x']
    y = request.args['y']
    return 'The product is ' + str(int(x)*int(y))

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

