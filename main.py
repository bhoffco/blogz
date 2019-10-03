from flask import Flask, request, redirect, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
import re
import os
import jinja2 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content

# posts = [
# {
#     'title': 'first post',
#     'content': 'this is the first post'
# },
# {
#     'title': 'second post',
#     'content': 'this is the second post'
# },
# {
#     'title': 'third post',
#     'content': 'this is the third post'
# }
# ]

# @app.route('/post/<?=post_id>')
# def post(post_id):

#     post = Blog.query.filter_by(id=post_id).one()

#     return render_template('post.html', title='Blog', post=post)

# @app.route('/post?id=42')
# def post():

#     blog_title = request.args.get('blog_title')
#     blog_content = request.args.get('blog_posts')
    

#     return render_template('post.html', blog_title=blog_title, blog_content=blog_content)

@app.route('/')
def index():
    posts = Blog.query.all()
    return render_template('blog.html', title="Blog", posts=posts)

@app.route('/blog', methods=['GET', 'POST'])
def blog_post():

    if request.args:
        
        id = request.args.get('id')
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html', title='Blog', posts=posts)

    else:
        posts = Blog.query.all()
        return render_template('blog.html', title='Blog', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newp():

    if request.method == 'GET':

        return render_template('newpost.html', title='Add Post')

    if request.method == 'POST':

        blog_title = request.form['blog_title']
        blog_content = request.form['blog_post']
        blog_post_error = ""
        
    if blog_title == "" or blog_content == "":

        blog_post_error = "Please complete all fields"

    if not blog_post_error:

        post = Blog(blog_title, blog_content)
        db.session.add(post)
        db.session.commit()
        return redirect('/blog?id={}'.format(post.id))

    else:

        return render_template('newpost.html', blog_post_error=blog_post_error, blog_title=blog_title, blog_content=blog_content)

            
 

if __name__ == '__main__':  
    app.run()