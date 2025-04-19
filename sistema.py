# Sistema de Empréstimo de Livros - Web App com Flask, SQLite e Cadastro de Usuário

from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave-secreta'

db = SQLAlchemy(app)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    autor = db.Column(db.String(100))
    categoria = db.Column(db.String(50))
    disponivel = db.Column(db.Boolean, default=True)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    matricula = db.Column(db.String(20), unique=True)
    senha_hash = db.Column(db.String(100))

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data_emprestimo = db.Column(db.DateTime, default=datetime.utcnow)
    data_devolucao = db.Column(db.DateTime)
    devolvido = db.Column(db.Boolean, default=False)

    livro = db.relationship('Livro', backref=db.backref('emprestimos', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('emprestimos', lazy=True))

@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    livros = Livro.query.all()
    return render_template('index.html', livros=livros, usuario_id=session['usuario_id'])

@app.route('/emprestar/<int:livro_id>/<int:usuario_id>')
def emprestar(livro_id, usuario_id):
    if 'usuario_id' not in session or session['usuario_id'] != usuario_id:
        return redirect(url_for('login'))
    livro = Livro.query.get(livro_id)
    usuario = Usuario.query.get(usuario_id)
    if livro and livro.disponivel:
        livro.disponivel = False
        emprestimo = Emprestimo(
            livro=livro,
            usuario=usuario,
            data_devolucao=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(emprestimo)
        db.session.commit()
        return redirect(url_for('index'))
    return 'Livro indisponível ou usuário inválido.'

@app.route('/devolver/<int:emprestimo_id>')
def devolver(emprestimo_id):
    emprestimo = Emprestimo.query.get(emprestimo_id)
    if emprestimo and not emprestimo.devolvido:
        emprestimo.devolvido = True
        emprestimo.livro.disponivel = True
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        matricula = request.form['matricula']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(matricula=matricula).first()
        if usuario and usuario.verificar_senha(senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('index'))
        flash('Matrícula ou senha inválida.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        senha = request.form['senha']
        if Usuario.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada.')
            return redirect(url_for('cadastro'))
        novo_usuario = Usuario(nome=nome, matricula=matricula)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
