import os
from helpers import login_required
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

url = os.environ['DATABASE_URL']
secret_key = os.environ['SECRET_KEY']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    passw = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(40), nullable=False)

db.create_all()

u = User.query.filter_by(login='admin').first()
if u is None:
    admin = User(login="admin", passw="admin", nome="Administrador")
    db.session.add(admin)
    db.session.commit()


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

@app.route("/login/", methods=['GET', 'POST'])
def login():

    if request.method == 'GET' :
        return render_template('login.html')
    if request.method == 'POST' :
        u = User.query.filter_by(login=request.form['login'], 
                                 passw=request.form['passw']).first()
        if u is None:
            return render_template("login.html", error="Usuário ou senha inválidos.")
        else:
            session['user_id'] = u.id
            return redirect("/")

if __name__ == '__main__':
	app.run(debug=True)
