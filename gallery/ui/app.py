from flask import Flask
from flask import request
from flask import render_template

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

@app.route('/goodbye')
def goodbye():
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
