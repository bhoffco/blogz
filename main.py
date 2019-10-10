from flask import Flask, request, redirect, render_template, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re
import os
import jinja2   
import hashlib



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'akjhfksnjlkansf884b&&$#(9kkdkh)dfdfsdfsdfsdsd'

db = SQLAlchemy(app)

def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
    
    return False

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    user_posts = db.relationship('Blog', backref='owner')
    
    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allow_routes = ['login', 'register', 'static', 'index']
    if request.endpoint not in allow_routes and 'email' not in session:
        return redirect('/login')


@app.route('/')
def index():
    
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        user_error = ""
        password_error = ""
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            return redirect('/newpost')
        if user and check_pw_hash(password, user.pw_hash) != password:
            password_error = "Password is incorrect"
            return render_template('login.html', email=email, password_error=password_error)
        else:
            # todo - explain why login failed
            user_error = "User does not exist"
            return render_template('login.html', user_error=user_error)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        email_error = ""
        password_error = ""
        verify_error = ""
        user_exists_error = ""

        existing_user = User.query.filter_by(email=email).first()

        email_match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

        # todo validate user data 
        if len(email) < 3 or len(email) > 40 or email_match == None:
	        email_error = "Your email is not valid"

        if existing_user and not email_error:
            user_exists_error = "Duplicate user"
            return render_template('signup.html', email=email, user_exists_error=user_exists_error)
        

        elif len(password) < 3 or len(password) > 20:
            password_error = "Your password must be at least 3 characters"

        elif verify != password:
            verify_error = "Your passwords did not match"


        elif not existing_user and not email_error and not password_error and not verify_error:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        

        return render_template('signup.html', email_error=email_error, email=email, password=password, password_error=password_error, verify_error=verify_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

@app.route('/blog', methods=['GET', 'POST'])
def blog_post():
    logout = ""

    if 'id' in request.args:
        
        id = request.args.get('id')
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html', title='Blog', posts=posts, logout=logout)

    elif "user" in request.args:
        user_id = request.args.get('user')
        posts = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('blog.html', title = 'Blog', posts=posts)

    else:
        posts = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blog.html', title='Blog', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newp():

    if request.method == 'GET':

        return render_template('newpost.html', title='Add Post')

    if request.method == 'POST':

        blog_title = request.form['blog_title']
        owner = User.query.filter_by(email=session['email']).first()
        blog_content = request.form['blog_post']
        blog_post_error = ""
        
    if blog_title == "" or blog_content == "":

        blog_post_error = "Please complete all fields"

    if not blog_post_error:

        post = Blog(blog_title, blog_content, owner)
        db.session.add(post)
        db.session.commit()
        return redirect('/blog?id={}'.format(post.id))

    else:

        return render_template('newpost.html', blog_post_error=blog_post_error, blog_title=blog_title, blog_content=blog_content)

if __name__ == '__main__':  
    app.run()