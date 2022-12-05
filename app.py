import os
import flask
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request,  render_template, session, redirect, url_for
from flask_migrate import Migrate

from dotenv import load_dotenv
from flask_mail import Mail, Message
from datetime import datetime

from argon2 import PasswordHasher

# from models import User, Post

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

# naming convention
metadata = MetaData(
    naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# create the extension
db = SQLAlchemy(app, metadata=metadata)

# Add flask migrate to update the database whenever you change the Models
migrate = Migrate(app, db)

# initialize the app with the extension
db.init_app(app)

# Mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_ADDRESS')
app.config['MAIL_PASSWORD'] = os.environ.get('PASSCODE')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'EMAIL_ADDRESS'

"""
     Usually you need 587 with STARTTLS and 465 with SSL.
     i.e when app.config['MAIL_PORT']=465 THEN set app.config['MAIL_USE_SSL'] = True and app.config['MAIL_USE_TLS']=False
    OTHERWISE
     when app.config['MAIL_PORT']=587 THEN set app.config['MAIL_USE_SSL'] = False and app.config['MAIL_USE_TLS']=True
    IN SHORT
        TLS runs on port 587 while SSL runs on port 465
    As at my current limited knowledge the two cannot be set to True at the same time
"""

mail = Mail(app)


# MODELS
# User Model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    post = db.relation("Post", back_populates="author")

    def __repr__(self):
        return f'{self.username} + {self.email} + {self.password}'


# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())
    author = db.relationship("Author", back_populates="post", lazy="selectin")
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    category = db.relationship("Category", back_populates="post")
    comments = db.relationship("Comments", back_populates="post")

    def __repr__(self):
        return f'{self.post} {self.created_at}'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    post = db.relationship("Post", back_populates="category")

    def __repr__(self):
        return f'{self.name}'


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    comment = db.Column(db.String, nullable=False)
    post = db.relationship("Post", back_populates="comments")

    def __repr__(self):
        return f'username: {self.username}, email: {self.email}, comment: {self.comment}'


"""
    # From here we run >flask shell from the terminal
    # THEN  >from app import db
    # THEN  > db.create_all()



If you're using a python shell instead of flask shell, you can push a context manually. flask shell will handle that for you.

>>> from project import app, db
>>> app.app_context().push()
>>> db.create_all()

##### doing it manually (using python shell) like in case one above will yield errors
"""


@app.route("/", methods=["GET"])
def index():
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars()
    return render_template('index.html', categories=categories)


@app.route("/blog/", methods=["GET", "POST"])
def blog():
    return render_template('blog/blog.html')


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    # Get form data
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    ph = PasswordHasher()

    if not email or not password:
        message = "Kindly fill in all the fields"
        return render_template("Auth/login.html", message=message)

    if request.method == "POST":
        try:
            user = Author.query.filter_by(email=email).first()
            verify_password = ph.verify(user.password, password)

            if not user or verify_password == False:
                # return redirect(url_for("blog", name=user.username))
                message = "Either password or email is incorrect, try again!"
                return render_template("Auth/login.html", message=message)
            else:
                return render_template("blog/blog.html", name=user.username)
        # if the above check passes, then we know the user has the right credentials
        except:
            render_template("Auth/login.html", message="Something went wrong")

    return render_template("Auth/login.html")


@app.route('/register', methods=["GET", "POST"])
def signup():
    # Get form data
    name = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    ph = PasswordHasher()

    if not name or not email or not password:
        message = "Kindly fill in all the fields"
        return render_template('Auth/register.html', message=message)

    if request.method == "POST":
        # Store user details to database
        user = Author(username=name, email=email, password=ph.hash(password))
        db.session.add(user)
        db.session.commit()

        # Notify the user via email that he/she has been successfully registered
        msg = Message('Thanks for Registering!', recipients=[email])
        msg.html = f"<h3 style='color:blue;'>" \
            f"Hello <span style='color:green;'>{name}</span>, details registered successfully! Welcome to my blog</h3>"
        mail.send(msg)

        # Take the user to login page if all is successful
        return redirect(url_for("login"))

    return render_template('./Auth/register.html')


@app.route('/post', methods=['GET', 'POST'])
def publish_blog():
    return render_template('blog/post.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')


if __name__ == '__main__':
    app.run(debug=True)
