from datetime import datetime
from flask import Flask, flash, url_for
from flask import render_template, redirect, request
from flask import send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_login import current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, ContactForm

""" Setting up Flask """
app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = '1cc7a427c58c3837322687b7ff4ee836'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

""" Dictionary to make things easier to customize """
info = {
'company_name': 'Bedrift AS',
'current_tab' : None,
}


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email  = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref="author", lazy=True)
    
    def validate_password(self, password):
        return bcrypt.verify(password, self.password)
    
    def __repr__(self):
        return self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,)
    
    def __repr__(self):
        return self.title

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email  = db.Column(db.String(120), nullable=False)
    name  = db.Column(db.String(120), nullable=False)
    inquiry  = db.Column(db.String(200), nullable=False)
    


""" Home / Forside """
@app.route("/home")
def home():
    info['current_tab'] = 'home'
    return render_template('home.html',info=info)

""" Products / Produkter """
@app.route("/products")
def products():
    info['current_tab'] = 'products'
    return render_template('products.html',info=info)

""" About us / Om oss """
@app.route("/aboutus")
def about_us():
    info['current_tab'] = 'about_us'
    return render_template('about_us.html',info=info)

""" List users / vise hvilke brukere som er opprettet på systemet """
@app.route("/users")
def users():
    info['current_tab'] = 'users'
    return render_template('users.html',info=info, users=User.query.all())

""" List inquiries / vise hendvendelser (generert fra kontakt-oss) """
@app.route("/hendvendelser")
def inquiries():
    info['current_tab'] = 'inquiries'
    return render_template('inquiries.html', info=info,inquiries=Inquiry.query.all())

""" Contact us - lage nye hendvendelser aka "Kontakt oss" """
@app.route("/contact", methods=['GET','POST'])
def contact():
    info['current_tab'] = 'contact'
    form = ContactForm()
    if request.method == "POST" and form.validate():
        i = Inquiry(
            email=form.email.data,
            inquiry = form.inquiry.data,
            name = form.name.data )
        db.session.add(i)
        db.session.commit()
        flash("Takk for din henvendelse!",category="success")
    elif request.method == "POST" and not form.validate():
        flash("Pass på at du har fylt ut kontaktskjemaet riktig.", category="warning")
    return render_template('contact.html',form=form,info=info)

""" User-registration - Lage nye brukere """
@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    info['current_tab'] = 'register'
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        if len(User.query.filter_by(username=form.username.data).all()) > 0:
            flash('Username already exists, please pick another one.',
                  category="danger")
            return render_template('register.html',
                title="Register",
                form = form,
                info = info)
        if len(User.query.filter_by(email=form.email.data).all()) > 0:
            flash('Email address already exists, please pick another one.',
                  category="danger")
            return render_template('register.html',
                title="Register",
                form = form,
                info = info)
        u = User(
            username = form.username.data,
            email = form.email.data,
            password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8'))
        db.session.add(u)
        db.session.commit()
        flash(f'Konto opprettet for {form.username.data}!', category="success")
        login_user(u)
        return redirect(url_for('home'))
    elif request.method == 'POST' and not form.validate():
        flash(f'Ugyldig data, sjekk feil under', category="danger")
        print(form.errors)
    return render_template('register.html',
        title="Register",
        form = form,
        info = info)

""" User authentication / login-side """
@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))    
    info['current_tab'] = 'login'
    form = LoginForm()
    
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        hashedpw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        if not user:
            flash(f'User with email {form.email.data} does not exist.')
            render_template('login.html', title="Login", form = form, info = info)
        elif user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user,remember=form.remember.data)
                flash(f'Velkommen tilbake {user.username}!', category='success')
                return redirect(url_for('home'))
    return render_template('login.html',
        title="Login", form = form, info = info)

""" Logout / logge ut """
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

""" Serving static files like JS, CSS and images """
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

""" Root (/) (redirect to home) """
@app.route("/")
def redir_home():
    return redirect("/home")

""" Helper-function for flask_login  """
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

""" Start app if this file is run directly """
if __name__ == "__main__":
    app.run(debug=True)




