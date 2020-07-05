from flask import Flask
from flask import request
from flask import redirect
from flask import session 
from functools import wraps
import os


import psycopg2

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

def check_admin():
    return 'username' in session and session['username'] == 'mickey'

def connect():
    global connection
#   secret = get_secret()
#   connection = psycopg2.connect(host=get_host(secret), dbname=get_dbname(secret), user=get_username(secret), password=get_password(secret))
    if os.getenv("IG_PASSWD_FILE") == None:
        password = os.getenv("IG_PASSWD")
    else:
        with open(os.getenv("IG_PASSWD_FILE"), "r") as file:
            password = file.read().rstrip()
            
    print("PG_HOST", os.getenv("PG_HOST"))
    print("PG_PORT", os.getenv("PG_PORT"))
    print("IG_DATABASE", os.getenv("IG_DATABASE"))
    print("IG_USER", os.getenv("IG_USER"))
    print("IG_PASSWD", os.getenv("IG_PASSWD"))
    connection = psycopg2.connect(host=os.getenv("PG_HOST"), port=os.getenv("PG_PORT"), dbname=os.getenv("IG_DATABASE"), user=os.getenv("IG_USER"), password=password)

def execute(query,args=None):
    global connection
    cursor = connection.cursor()
    if not args:
        cursor.execute(query)
    else:
        cursor.execute(query, args) 
    connection.commit()   
    return cursor

def get_user_by_username(username):
    return execute("select * from users where username=%s", (username,)).fetchone()

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

def requires_admin(view):
    @wraps(view)
    def decorated(**kwargs):
        if not check_admin():
            return redirect('/login')
        return view(**kwargs)
    return decorated

@app.route('/invalidlogin')
def invalidLogin():
    return """
<!DOCTYPE html>
<html>
    <head>
        <title>Login</title>
        <meta charset="utf-8" />
    </head>
    <body>
        <h1>Invalid Login</h1>
        <form action="/login" method="POST">
          Username: <input name="username" value="" /><br />
          Password: <input type="password" name="password" value="" /><br />
          <input type="submit" value="Login" />
          </form>
    </body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        row = get_user_by_username(request.form["username"])
        if row is None or row[1] != request.form["password"]:
            return redirect('/invalidLogin')
        else:
            session['username'] = request.form["username"]
            return redirect("/debugSession")
    else:
        return """
<!DOCTYPE html>
<html>
    <head>
        <title>Login</title>
        <meta charset="utf-8" />
    </head>
    <body>
        <h1>Login</h1>
        <form action="/login" method="POST">
          Username: <input name="username" value="" /><br />
          Password: <input type="password" name="password" value="" /><br />
          <input type="submit" value="Login" />
          </form>
    </body>
</html>
"""

@app.route('/debugSession')
def debugSession():
    result = ""
    for key,value in session.items():
        result += key+"->"+str(value)+"<br />"
    return result


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
        <h1>Test - Christian Nightingale's Auburn Python Web App</h1>
    </body>
</html>
"""
@app.route('/admin', methods = ['GET'])
@requires_admin
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
        <form action="/admin/add_user" method="GET">
            <input type="submit" value="Add User">
        </form>
    </body>
</html>
"""
    return html

@app.route('/admin/add_user', methods = ['GET'])
@requires_admin
def user_add():
    return """
<html>
    <head>
        <title>Add User</title>
    </head>
    <body>
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

@app.route('/admin/add', methods = ['POST'])
@requires_admin
def user_add_post():
    add_user(request.form["username"], request.form["password"], request.form["full_name"])
    return redirect('/admin')

@app.route('/admin/edit/<username>', methods = ['GET', 'POST'])
@requires_admin
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
@requires_admin
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