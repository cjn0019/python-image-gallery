from flask import Flask
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
    return 'Nice to meet you' + name

