from flask import Flask
from flask import request
from flask import render_template
from flask import redirect

import psycopg2
import json
#from gallery.tools.db import get_username
## from secrets import get_secret_image_gallery

connection = None

# def get_secret():
#     jsonString = get_secret_image_gallery()
#     return json.loads(jsonString)
#  
# def get_password(secret):
#     return secret['password']
#  
# def get_host(secret):
#     return secret['host']
#  
# def get_username(secret):
#     return secret['username']
#  
# def get_dbname(secret):
#     return secret['database_name']

def connect():
    global connection
#   secret = get_secret()
#   connection = psycopg2.connect(host=get_host(secret), dbname=get_dbname(secret), user=get_username(secret), password=get_password(secret))
    connection = psycopg2.connect(host="image-gallery.cvii1d1fvgqo.us-west-1.rds.amazonaws.com", dbname="image_gallery", user="image_gallery", password="(9!1bT=*lgmKkeFu#8<HlxyXJ&|W$Y]G")

def execute(query,args=None):
    global connection
    cursor = connection.cursor()
    if not args:
        cursor.execute(query)
    else:
        cursor.execute(query, args) 
    connection.commit()   
    return cursor

def user_exists(username):
    if execute("SELECT * FROM users WHERE username=%s;",(username,)).rowcount == 0: 
        return False
    else: 
        return True

def get_users():
    return execute('SELECT * FROM users')

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
    
connect()

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
@app.route('/admin', methods = ['GET'])
def users():
    html = """
<html>
    <head>
        <title>List Users</title>
    </head>
    <body>
        <table>
            <tr>
                <th>Username</th>
                <th>Full Name</th>
                <th></th>
            </tr>
"""

    for user in get_users():
        html += '<tr>'
        html += '<td><a href="/admin/edit/{}">{}</a></td>'.format(user[0], user[0])
        html += '<td>' + user[2] + '</td>'
        html += '<td><a href="/admin/delete/{}">delete</a></td>'.format(user[0])
        html += '</tr>'

    html += """
        </table>
        <br><br>
        <form action="/admin/add" method="POST">
            Username:  <input type="text" name="username"><br>
            Password:  <input type="text" name="password"><br>
            Full name: <input type="text" name="full_name"><br>
            <br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
</html>
"""
    return html

@app.route('/admin/add', methods = ['POST'])
def user_add_post():
    add_user(request.form["username"], request.form["password"], request.form["full_name"])
    return redirect('/admin')

@app.route('/admin/edit/<username>', methods = ['GET', 'POST'])
def user_edit(username):
    if request.method == "GET":
        return """
<html>
    <head>
        <title>Edit User </title>
    </head>
    <body>
        <form action="/admin/edit/{}" method="POST">
            <input type="hidden" name="username" value="{}"><br>
            Password:  <input type="password" name="password"><br>
            Full Name: <input type="text" name="full_name"><br>
            <input type="submit" value="Submit">
        </form>
    </body>
</html>
""".format(username, username)
    else:
        edit_user(request.form["username"], request.form["password"], request.form["full_name"])
    return redirect('/admin')

@app.route('/admin/delete/<username>', methods=['GET', 'POST'])
def user_delete(username):
    if request.method == 'GET':
        return """
    <html>
        <head>
            <title>Delete User</title>
        </head>
        <body>
            Are you sure you want to delete user {}?
            <form action="/admin/delete/{}" method="POST">
                <input type="submit" value="Yes">
            </form>
            <form action="/admin" method="GET">
                <input type="submit" value="No">
            </form>
        </body>
    </html>
    """.format(username, username)
    else:
        delete_user(username)
        return redirect('/admin')