from datetime import datetime
from flask import Flask, flash, url_for
from flask import render_template, redirect
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm

app = Flask(__name__,
    template_folder="templates")
app.config['SECRET_KEY'] = '1cc7a427c58c3837322687b7ff4ee836'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email  = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), unique=True, nullable=False, default='default.jpg')
    password = db.Column(db.String(60), unique=True, nullable=False)
    posts = db.relationship('Post',
        backref="author",
        lazy=True)

    def __repr__(self):
        return self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,)
    def __repr__(self):
        return self.title
info = {
'company_name': 'Bedrift AS',
}

#Serving static files like JS and CSS
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/")
def redir_home():
    return redirect("/home")

@app.route("/home")
def home():
    return render_template('home.html',info=info)

@app.route("/products")
def products():
    return render_template('products.html',info=info)

@app.route("/aboutus")
def about_us():
    return render_template('about_us.html',info=info)


@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Konto opprettet for {form.username.data}!')
        return redirect(url_for('home'))
    return render_template('register.html',
        title="Register",
        form = form,
        info = info)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    return render_template('login.html',
        title="Login",
        form = form,
        info = info)











if __name__ == "__main__":
    app.run(debug=True)








"""
@app.route("/base")
def base():
    return render_template('base.html')
"""
