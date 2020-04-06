import os
from flask import Flask, render_template, request, make_response, session, escape, redirect, url_for, flash, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import tools

dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + '/users_database.db'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'contraseñasecreta'

secret_key = 'contraseñasecreta'

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    invite   = db.Column(db.String(20), unique=True, nullable=False)
    level    = db.Column(db.Integer, nullable=False)

@app.before_request
def before_request():
    if 'username' in session:
        g.user = session['username']
        g.loged = True
        g.level = tools.get_user_level(f'{g.user}')
    else:
        g.user = None
    g.ip = request.remote_addr

@app.route('/')
def home():
    if g.user:
        return render_template('home.html')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if not g.user:
        if request.method=='POST':
            hashed_pw = generate_password_hash(request.form['password'], method='sha256')
            
            nivel = tools.check_invite(f"{request.form['invite']}")
            
            if nivel == 'normal':
                new_user = Users(username=request.form['username'].lower(), password=hashed_pw, invite=request.form['invite'], level=0)
            elif nivel == 'admin':
                new_user = Users(username=request.form['username'].lower(), password=hashed_pw, invite=request.form['username'], level=1)
            else:
                return render_template('error.html', error='El código de invitación es inválido')

            try:
                db.session.add(new_user)
                db.session.commit()
            except Exception as EX:
                return render_template('error.html', error="Ya hay un usuario registrado con ese nombre.")

            return redirect(url_for('login'))

        return render_template('register.html')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET','POST'])
def login():
    if not g.user:
        if request.method=='POST':
            user = Users.query.filter_by(username=request.form['username'].lower()).first()

            if user and check_password_hash(user.password, request.form['password']):
                session["username"] = user.username
                return redirect(url_for('home'))

            return render_template('error.html', error='La clave es incorrecta.')

        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if g.user:
        session.pop('username', None)

        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/admin/panel/<password>')
def adminPanel(password):
    if g.user and g.level == 1 and password == 'clavesupersecreta':
        normal, admins = tools.get_users()
        return render_template('panel.html', admins=admins, normal=normal, username=g.user)
    return render_template('error.html', error='You cannot enter this page.')

@app.route('/invites/<action>', methods=['GET', 'POST'])
def invites(action):
    if g.user and g.level == 1:
        if request.method == 'POST':
            if action == 'generar':
                try:
                    tools.generate_invites('add', cant=int(request.form['cantidad']))
                    tools.LOG(usuario=g.user, ip=g.ip, log=f'Se ha(n) creado {request.form["cantidad"]} invitacion(es).')
                    return redirect(url_for('adminPanel', password='clavesupersecreta'))
                except Exception as EX:
                    tools.errorLOG(EX)
                    return render_template('error.html', error='An error occurred while trying to generate the invitations, it has been saved in the error LOG file.')

            elif action == 'eliminar':
                try:
                    tools.generate_invites(action='delete')
                    tools.LOG(usuario=g.user, ip=g.ip, log=f'Se han eliminado todas las invitaciones.')
                    return redirect(url_for('adminPanel', password='clavesupersecreta'))
                except Exception as EX:
                    tools.errorLOG(EX)
                    return render_template('error.html', error='An error occurred while trying to delete the invitations, it has been saved in the error LOG file.')
            else:
                return render_template('error.html', error='¯\_(ツ)_/¯')
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/user/<user>', methods=['GET', 'POST'])
def user(user):
    if g.user and g.level == 1:
        if request.method == 'POST':
            if user == 'delete all':
                try:
                    tools.delete_database()
                    tools.LOG(usuario=g.user, ip=g.ip, log=f'Se ha eliminado toda la base de datos.')
                    return redirect(url_for('adminPanel', password='clavesupersecreta'))
                except Exception as EX:
                    tools.errorLOG(EX)
                    return render_template('error.html', error='An error occurred while trying to delete all, it has been saved in the error LOG file.')

            for key in request.form:
                if key.startswith('delete'):
                    try:
                        tools.delete_user(user)
                        tools.LOG(usuario=g.user, ip=g.ip, log=f'Se ha eliminado al usuario {user}.')
                        return redirect(url_for('adminPanel', password='clavesupersecreta'))
                    except Exception as EX:
                        tools.errorLOG(EX)
                        return render_template('error.html', error='An error occurred while trying to delete the user, it has been saved in the error LOG file.')

                elif key.startswith('upgrade'):
                    try:
                        tools.make_admin(user)
                        tools.LOG(usuario=g.user, ip=g.ip, log=f'Se ha hecho administrador al usuario {user}.')
                        return redirect(url_for('adminPanel', password='clavesupersecreta'))
                    except Exception as EX:
                        tools.errorLOG(EX)
                        return render_template('error.html', error='An error occurred while trying to upgrade the user, it has been saved in the error LOG file.')

                elif key.startswith('downgrade'):
                    try:
                        tools.make_normal(user)
                        tools.LOG(usuario=g.user, ip=g.ip, log=f'Se ha quitado permisos al usuario {user}.')
                        return redirect(url_for('adminPanel', password='clavesupersecreta'))
                    except Exception as EX:
                        tools.errorLOG(EX)
                        return render_template('error.html', error='An error occurred while trying to downgrade the user, it has been saved in the error LOG file.')

                else:
                    return render_template('error.html', error='An error occurred, it has been saved in the error LOG file.')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)