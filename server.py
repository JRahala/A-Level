from operator import truediv
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("template.html")

@app.route("/register_login/")
def register_login():
    return render_template("register_login.html")

app.run(host = "0.0.0.0", port = 8080, debug = True)

