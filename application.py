import os
import json
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
    email = db.Column(db.String(50), unique=True, nullable=False)
    passw = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.Integer, nullable=False)


class Raca(db.Model):
    __tablename__ = 'racas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), unique=True, nullable=False)
    idade_adulto = db.Column(db.Integer, nullable=False)
    idade_max = db.Column(db.Integer, nullable=False)
    tendencia = db.Column(db.Text)
    tam_min = db.Column(db.Float, nullable=False)
    tam_max = db.Column(db.Float, nullable=False)
    desloc = db.Column(db.Float, nullable=False)
    desloc_armadura = db.Column(db.Float, nullable=False)
    incs_hab = db.relationship('Inc_Habilidade', backref='racas', lazy=True)

class Habilidade(db.Model):
    __tablename__ = 'habilidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    desc = db.Column(db.Text)
    incs = db.relationship('Inc_Habilidade', backref='habilidades', lazy=True)

class Inc_Habilidade(db.Model):
    __tablename__ = 'inc_habilidade'
    id = db.Column(db.Integer, primary_key=True)
    id_habilidade = db.Column(db.Integer, db.ForeignKey('habilidades.id'),
                              nullable=False)
    id_raca = db.Column(db.Integer, db.ForeignKey('racas.id'), nullable=False)
    nome = db.Column(db.String(20), nullable=False)
    acrescimo = db.Column(db.Integer, nullable=False)


db.create_all()

u = User.query.filter_by(login='admin').first()
if u is None:
    admin = User(login="admin", passw="admin", tipo=1, nome="Administrador", email="admin@admins")
    db.session.add(admin)
    db.session.commit()


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
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


@app.route('/raca/', methods=['GET', 'POST'])
def raca():

    if request.method == 'GET' :
        rows = Raca.query.all()
        return render_template('raca.html', rows=rows)
    if request.method == 'POST' :
        rows = Raca.query.all()

        nome = request.form["nome"]
        idade_adulto = request.form["idade_adulto"]
        idade_max = request.form["idade_max"]
        tendencia = request.form["tendencia"]
        tam_min = request.form["tam_min"]
        tam_max = request.form["tam_max"]
        desloc = request.form["desloc"]
        desloc_armadura = request.form["desloc_armadura"]

        r = Raca.query.filter_by(nome=nome)
        if not r is None:
            return render_template('raca.html',
                                   rows=rows, 
                                   error="Raça %s ja cadastrada." % (nome),
                                   nome=nome,
                                   idade_adulto=int(idade_adulto),
                                   idade_max=int(idade_max),
                                   tendencia=tendencia,
                                   tam_min=int(tam_min),
                                   tam_max=int(tam_max),
                                   desloc=float(desloc),
                                   desloc_armadura=float(desloc_armadura))


        raca = Raca(nome=nome,
                    idade_adulto=int(idade_adulto),
                    idade_max=int(idade_max),
                    tendencia=tendencia,
                    tam_min=int(tam_min),
                    tam_max=int(tam_max),
                    desloc=float(desloc),
                    desloc_armadura=float(desloc_armadura))
        db.session.add(raca)
        db.session.commit()
        
        return render_template('raca.html', rows=rows, success="Raça cadastrado com sucesso!!!")


@app.route('/raca_json/<id>', methods=['GET'])
def raca_json(id):
    # id = request.form["id"]
    raca = Raca.query.filter_by(id=id).first()
    incs = Inc_Habilidade.query.filter_by(id_raca=Raca.id).all()
    iss = []
    for inc in incs:
        hab = Habilidade.query.filter_by(id=inc.id).first()
        i = {
            "id": inc.id,
            "habilidade": hab.nome,
            "nome": inc.nome,
            "acrescimo": inc.acrescimo
        }
        iss.append(i)



    r = {
        "id": raca.id,
        "nome": raca.nome,
        "idade_adulto": raca.idade_adulto,
        "idade_max": raca.idade_max,
        "tendencia": raca.tendencia,
        "tam_min": raca.tam_min,
        "tam_max": raca.tam_max,
        "desloc": raca.desloc,
        "desloc_armadura": raca.desloc_armadura,
        "incs_hab": iss
    }
    print(json.dumps(r))
    return json.dumps(r)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
