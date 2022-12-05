from app import app
from flask_sqlalchemy import SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy()
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
# initialize the app with the extension
db.init_app(app)


# TODO 1
# Add a model
# Use SQLAlchmy as my orm to manipulate data
# Use SQLite3 as my db to store data

# TODO 2
# Ass a login form
# Add a registration form
# Redirect users to blog
#
# # User Model
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(30), unique=True, nullable=False)
#     email = db.Column(db.String, unique=True, nullable=False)
#     password = db.Column(db.String, nullable=False)
#     posts = db.relationship("Post", backref="user", lazy=True)
#     created_at = db.Column(db.DateTime)
#
#     def __repr__(self):
#         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
#
#
# # Post Model
# class Post(app.db.Model):
#     __tablename__ = "posts"
#     id = db.Column(db.Integer, primary_key=True)
#     post = db.Column(db.String, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # declaring foreign keys
#     user = db.relationship("User", backref="posts", lazy=True) # creating relationship
#     created_at = db.Column(db.DateTime)
#
#     def __repr__(self):
#         return f'Address(id={self.id!r}, email={self.email_address!r})'
