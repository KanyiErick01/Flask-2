#imports
from flask import Flask,url_for,render_template,redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField 
from wtforms.validators import DataRequired, Length, Email 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

#configs
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urbans.db"
db=SQLAlchemy(app)
migrate = Migrate(app, db,command='migrate',render_as_batch=False)
app.config['SECRET_KEY'] = 'your_secret_key'
bcrypt = Bcrypt(app) 
admin=Admin(app)

#Login function
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#routes
@app.route("/", methods=["POST","GET"])
def index():
    return render_template ("index.html")

@app.route("/login", methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
    
        flash("Login Successfull!")
        return redirect (url_for('signup'))

    return render_template('login.html', form=form)

@app.route("/signup", methods=["POST","GET"])
def signup():
    form=SignUpForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect (url_for("login"))
    
    return render_template('signup.html', form=form)

@app.route("/blog", methods=["POST","GET"])
def posts():
    posts=Posts.query.order_by(Posts.date_created.desc()).all()
    return render_template("blog.html",posts=posts)

#@app.route('/admin')
#def admin():
    id=current_user.id
    if id== 1:
        return render_template("admin.html")
    else:
        flash("Sorry Admins Only!")
        return redirect(url_for("/"))

@app.route('/logout', methods=["POST","GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

#models
class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String,unique=True)
    email=db.Column(db.String,unique=True)
    password=db.Column(db.String,nullable=False)

    def __repr__(self):
        return self.username

class Posts(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String)
    date_created=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content=db.Column(db.Text)

    def __repr__(self):
        return self.title
    
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Posts, db.session))   

class ModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    
#forms
class LoginForm(FlaskForm):
    username=StringField('username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    submit=SubmitField('Login')

class SignUpForm(FlaskForm):
    username=StringField('username', validators=[DataRequired()])
    email=StringField('Email', validators=[DataRequired(), Email()])
    password=PasswordField('Password', validators=[DataRequired()]) 
    
    submit=SubmitField('Sign Up')


if __name__== "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)